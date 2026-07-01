"""
Modal app: IDM-VTON virtual try-on (https://github.com/yisol/IDM-VTON).

Unlike the old local VITON-HD integration, IDM-VTON generates its own
human-parse / pose / DensePose per request, so it needs no precomputed
per-image dataset artifacts and works on arbitrary uploaded photos too.

Deploy with:
    modal deploy modal_apps/idm_vton_app.py

Prints a URL like https://<workspace>--revera-idm-vton-idmvton-tryon.modal.run
Put that in .env as MODAL_VTON_URL. Protect it with a Modal proxy auth token
(https://modal.com/settings/proxy-auth-tokens) and put the Token ID / Secret
in .env as MODAL_PROXY_TOKEN_ID / MODAL_PROXY_TOKEN_SECRET.

Image build notes (read before touching this file):
- IDM-VTON's own `gradio_demo/detectron2` folder is a vendored, precompiled
  copy (`_C.cpython-39-x86_64-linux-gnu.so`) tied to Python 3.9. Modal no
  longer supports 3.9 as a standalone Python, so that shortcut is out —
  instead we build detectron2 from source for Python 3.10 (matching
  torch==2.0.1+cu118, same pin IDM-VTON's own environment.yaml uses) with
  FORCE_CUDA=1 and TORCH_CUDA_ARCH_LIST set for L4 (Ada, compute 8.9) so the
  CUDA extensions build on Modal's GPU-less build workers. The vendored
  `gradio_demo/detectron2` dir is deleted after cloning so it can't shadow
  the real pip-installed package on sys.path; `gradio_demo/densepose` is
  pure Python (no compiled extension) and is kept/used as-is.
"""

import io
import os
import sys

import modal
from fastapi import File, Form, Response, UploadFile

app = modal.App("revera-idm-vton")

hf_cache_volume = modal.Volume.from_name("idm-vton-hf-cache", create_if_missing=True)
HF_CACHE_PATH = "/cache"

IDM_VTON_REPO = "https://github.com/yisol/IDM-VTON.git"
IDM_VTON_DIR = "/root/IDM-VTON"
HF_SPACE_CKPT_BASE = "https://huggingface.co/spaces/yisol/IDM-VTON/resolve/main/ckpt"

image = (
    modal.Image.from_registry("nvidia/cuda:11.8.0-devel-ubuntu22.04", add_python="3.10")
    .apt_install("git", "wget", "libgl1", "libglib2.0-0", "build-essential", "ninja-build")
    .pip_install(
        "torch==2.0.1",
        "torchvision==0.15.2",
        extra_index_url="https://download.pytorch.org/whl/cu118",
    )
    .pip_install(
        "accelerate==0.25.0",
        "transformers==4.36.2",
        "diffusers==0.25.0",
        "einops==0.7.0",
        "scipy==1.11.1",
        "opencv-python-headless",
        # preprocess/openpose/annotator's body/hand/face pose estimation
        # (a ControlNet-style OpenPose implementation) needs these directly;
        # they aren't pulled in by anything else we install.
        "scikit-image",
        "matplotlib",
        # gradio_demo/densepose (vendored DensePose project) needs these too.
        "av",
        "lvis",
        "onnxruntime==1.16.2",
        "fvcore",
        "cloudpickle",
        "omegaconf",
        "pycocotools",
        "iopath",
        "yacs",
        "tabulate",
        "portalocker",
        "Pillow",
        # Pinned: diffusers==0.25.0 imports huggingface_hub.cached_download,
        # removed in huggingface_hub>=0.26. 0.20.3 is the last line that has it.
        "huggingface_hub==0.20.3",
        "safetensors",
        "sentencepiece",
        "fastapi[standard]",
        "python-multipart",
    )
    # Build detectron2's CUDA extensions from source. FORCE_CUDA is required
    # because Modal's image-build workers have no GPU attached; without it
    # detectron2's setup.py silently skips the CUDA ops. TORCH_CUDA_ARCH_LIST
    # targets L4 (Ada Lovelace, compute capability 8.9) specifically.
    # --no-build-isolation is required: detectron2's setup.py imports torch at
    # build time, so it must see the torch already installed above rather than
    # pip's isolated (torch-less) build env.
    # CC/CXX are forced to gcc/g++: Modal's add_python standalone interpreter
    # was built with clang, so sysconfig reports clang++ as the default C++
    # compiler even though only g++ (via build-essential) is installed here.
    .env({"FORCE_CUDA": "1", "TORCH_CUDA_ARCH_LIST": "8.9", "CC": "gcc", "CXX": "g++"})
    .pip_install("setuptools", "wheel")
    .run_commands(
        "python -m pip install --no-build-isolation "
        "git+https://github.com/facebookresearch/detectron2.git"
    )
    .run_commands(f"git clone --depth 1 {IDM_VTON_REPO} {IDM_VTON_DIR}")
    # The repo's own gradio_demo/detectron2 is a precompiled cpython-39 copy;
    # remove it so it can't shadow the source-built package above on sys.path.
    .run_commands(f"rm -rf {IDM_VTON_DIR}/gradio_demo/detectron2")
    .run_commands(
        f"mkdir -p {IDM_VTON_DIR}/ckpt/densepose "
        f"{IDM_VTON_DIR}/ckpt/humanparsing "
        f"{IDM_VTON_DIR}/ckpt/openpose/ckpts",
        f"wget -q -O {IDM_VTON_DIR}/ckpt/densepose/model_final_162be9.pkl "
        f"{HF_SPACE_CKPT_BASE}/densepose/model_final_162be9.pkl",
        f"wget -q -O {IDM_VTON_DIR}/ckpt/humanparsing/parsing_atr.onnx "
        f"{HF_SPACE_CKPT_BASE}/humanparsing/parsing_atr.onnx",
        f"wget -q -O {IDM_VTON_DIR}/ckpt/humanparsing/parsing_lip.onnx "
        f"{HF_SPACE_CKPT_BASE}/humanparsing/parsing_lip.onnx",
        f"wget -q -O {IDM_VTON_DIR}/ckpt/openpose/ckpts/body_pose_model.pth "
        f"{HF_SPACE_CKPT_BASE}/openpose/ckpts/body_pose_model.pth",
    )
    .env(
        {
            "HF_HOME": f"{HF_CACHE_PATH}/huggingface",
            "PYTHONPATH": f"{IDM_VTON_DIR}:{IDM_VTON_DIR}/gradio_demo",
        }
    )
)

CATEGORY_MAP = {"upper_body", "lower_body", "dresses"}


@app.cls(
    image=image,
    gpu="L4",
    volumes={HF_CACHE_PATH: hf_cache_volume},
    timeout=600,
    # First cold start downloads ~30GB of SDXL weights (unet, vae, both text
    # encoders, image encoder, unet_encoder) into the cache volume before
    # @modal.enter() returns — that blows past Modal's default 300s startup
    # window. Every start after that is fast since the volume is cached.
    startup_timeout=1800,
    scaledown_window=300,
)
class IDMVton:
    @modal.enter()
    def load(self):
        import torch
        from diffusers import AutoencoderKL, DDPMScheduler
        from transformers import (
            AutoTokenizer,
            CLIPImageProcessor,
            CLIPTextModel,
            CLIPTextModelWithProjection,
            CLIPVisionModelWithProjection,
        )

        os.chdir(IDM_VTON_DIR)
        for p in (IDM_VTON_DIR, os.path.join(IDM_VTON_DIR, "gradio_demo")):
            if p not in sys.path:
                sys.path.insert(0, p)

        from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline
        from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref
        from src.unet_hacked_tryon import UNet2DConditionModel
        from preprocess.humanparsing.run_parsing import Parsing
        from preprocess.openpose.run_openpose import OpenPose

        self.device = "cuda"
        base_path = "yisol/IDM-VTON"

        unet = UNet2DConditionModel.from_pretrained(base_path, subfolder="unet", torch_dtype=torch.float16)
        unet.requires_grad_(False)
        tokenizer_one = AutoTokenizer.from_pretrained(base_path, subfolder="tokenizer", use_fast=False)
        tokenizer_two = AutoTokenizer.from_pretrained(base_path, subfolder="tokenizer_2", use_fast=False)
        noise_scheduler = DDPMScheduler.from_pretrained(base_path, subfolder="scheduler")
        text_encoder_one = CLIPTextModel.from_pretrained(base_path, subfolder="text_encoder", torch_dtype=torch.float16)
        text_encoder_two = CLIPTextModelWithProjection.from_pretrained(
            base_path, subfolder="text_encoder_2", torch_dtype=torch.float16
        )
        image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            base_path, subfolder="image_encoder", torch_dtype=torch.float16
        )
        vae = AutoencoderKL.from_pretrained(base_path, subfolder="vae", torch_dtype=torch.float16)
        unet_encoder = UNet2DConditionModel_ref.from_pretrained(
            base_path, subfolder="unet_encoder", torch_dtype=torch.float16
        )
        for m in (unet_encoder, image_encoder, vae, unet, text_encoder_one, text_encoder_two):
            m.requires_grad_(False)

        self.pipe = TryonPipeline.from_pretrained(
            base_path,
            unet=unet,
            vae=vae,
            feature_extractor=CLIPImageProcessor(),
            text_encoder=text_encoder_one,
            text_encoder_2=text_encoder_two,
            tokenizer=tokenizer_one,
            tokenizer_2=tokenizer_two,
            scheduler=noise_scheduler,
            image_encoder=image_encoder,
            torch_dtype=torch.float16,
        )
        self.pipe.unet_encoder = unet_encoder
        self.pipe.to(self.device)
        self.pipe.unet_encoder.to(self.device)

        self.parsing_model = Parsing(0)
        self.openpose_model = OpenPose(0)
        self.openpose_model.preprocessor.body_estimation.model.to(self.device)

        from torchvision import transforms

        self.tensor_transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5], [0.5])])

        hf_cache_volume.commit()

    @modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
    async def tryon(
        self,
        person: UploadFile = File(...),
        garment: UploadFile = File(...),
        garment_des: str = Form("a garment"),
        category: str = Form("upper_body"),
        denoise_steps: int = Form(30),
        seed: int = Form(42),
    ):
        import torch
        from detectron2.data.detection_utils import _apply_exif_orientation, convert_PIL_to_numpy
        from PIL import Image

        import apply_net
        from utils_mask import get_mask_location

        if category not in CATEGORY_MAP:
            category = "upper_body"

        person_bytes = await person.read()
        garment_bytes = await garment.read()

        human_img = Image.open(io.BytesIO(person_bytes)).convert("RGB").resize((768, 1024))
        garm_img = Image.open(io.BytesIO(garment_bytes)).convert("RGB").resize((768, 1024))

        keypoints = self.openpose_model(human_img.resize((384, 512)))
        model_parse, _ = self.parsing_model(human_img.resize((384, 512)))
        mask, _ = get_mask_location("hd", category, model_parse, keypoints)
        mask = mask.resize((768, 1024))

        human_img_arg = _apply_exif_orientation(human_img.resize((384, 512)))
        human_img_arg = convert_PIL_to_numpy(human_img_arg, format="BGR")

        args = apply_net.create_argument_parser().parse_args(
            (
                "show",
                "./configs/densepose_rcnn_R_50_FPN_s1x.yaml",
                "./ckpt/densepose/model_final_162be9.pkl",
                "dp_segm",
                "-v",
                "--opts",
                "MODEL.DEVICE",
                "cuda",
            )
        )
        pose_img = args.func(args, human_img_arg)
        pose_img = pose_img[:, :, ::-1]
        pose_img = Image.fromarray(pose_img).resize((768, 1024))

        with torch.no_grad(), torch.cuda.amp.autocast():
            prompt = f"model is wearing {garment_des}"
            negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality"
            with torch.inference_mode():
                (
                    prompt_embeds,
                    negative_prompt_embeds,
                    pooled_prompt_embeds,
                    negative_pooled_prompt_embeds,
                ) = self.pipe.encode_prompt(
                    prompt,
                    num_images_per_prompt=1,
                    do_classifier_free_guidance=True,
                    negative_prompt=negative_prompt,
                )

                cloth_prompt = f"a photo of {garment_des}"
                (prompt_embeds_c, _, _, _) = self.pipe.encode_prompt(
                    [cloth_prompt],
                    num_images_per_prompt=1,
                    do_classifier_free_guidance=False,
                    negative_prompt=[negative_prompt],
                )

                pose_tensor = self.tensor_transform(pose_img).unsqueeze(0).to(self.device, torch.float16)
                garm_tensor = self.tensor_transform(garm_img).unsqueeze(0).to(self.device, torch.float16)
                generator = torch.Generator(self.device).manual_seed(seed)

                images = self.pipe(
                    prompt_embeds=prompt_embeds.to(self.device, torch.float16),
                    negative_prompt_embeds=negative_prompt_embeds.to(self.device, torch.float16),
                    pooled_prompt_embeds=pooled_prompt_embeds.to(self.device, torch.float16),
                    negative_pooled_prompt_embeds=negative_pooled_prompt_embeds.to(self.device, torch.float16),
                    num_inference_steps=denoise_steps,
                    generator=generator,
                    strength=1.0,
                    pose_img=pose_tensor,
                    text_embeds_cloth=prompt_embeds_c.to(self.device, torch.float16),
                    cloth=garm_tensor,
                    mask_image=mask,
                    image=human_img,
                    height=1024,
                    width=768,
                    ip_adapter_image=garm_img,
                    guidance_scale=2.0,
                )[0]

        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
