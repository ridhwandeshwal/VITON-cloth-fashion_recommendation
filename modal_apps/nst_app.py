"""
Modal app: neural style transfer (Magenta arbitrary-image-stylization via TF-Hub).

Deploy with:
    modal deploy modal_apps/nst_app.py

Prints a URL like https://<workspace>--revera-nst-transfer.modal.run
Put that in .env as MODAL_NST_URL. Protect it with a Modal proxy auth token
(https://modal.com/settings/proxy-auth-tokens) and put the Token ID / Secret
in .env as MODAL_PROXY_TOKEN_ID / MODAL_PROXY_TOKEN_SECRET.
"""

import io
from pathlib import Path

import modal
from fastapi import File, Response, UploadFile

NST_MODEL_DIR = Path(__file__).resolve().parent / "assets" / "nst_model"

app = modal.App("revera-nst")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "tensorflow-cpu>=2.16,<3",
        "tensorflow-hub>=0.16",
        "numpy<2",
        "pillow",
        "fastapi[standard]",
        "python-multipart",
    )
    .add_local_dir(str(NST_MODEL_DIR), "/root/model", copy=True)
)


@app.function(image=image, cpu=2.0, memory=4096, timeout=120, scaledown_window=180)
@modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
async def transfer(content_img: UploadFile = File(...), style_img: UploadFile = File(...)):
    import numpy as np
    import tensorflow as tf
    import tensorflow_hub as hub
    from PIL import Image

    content_bytes = await content_img.read()
    style_bytes = await style_img.read()

    content_image = np.array(Image.open(io.BytesIO(content_bytes)).convert("RGB"))
    style_image = np.array(Image.open(io.BytesIO(style_bytes)).convert("RGB"))

    content_image = content_image.astype(np.float32)[np.newaxis, ...] / 255.0
    style_image = style_image.astype(np.float32)[np.newaxis, ...] / 255.0
    style_image = tf.image.resize(style_image, (256, 256))

    hub_module = hub.load("/root/model")
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = np.array(outputs[0])
    stylized_image = (stylized_image.reshape(stylized_image.shape[1:]) * 255).clip(0, 255).astype(np.uint8)

    buf = io.BytesIO()
    Image.fromarray(stylized_image).save(buf, format="JPEG")

    return Response(content=buf.getvalue(), media_type="image/jpeg")
