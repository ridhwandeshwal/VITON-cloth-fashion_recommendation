from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import subprocess
import sys

from backend.utils.run_kaggle import run_vton_pipeline
from backend.utils.recommendation import generate_recommendations
from backend.utils.quiz_recommender import generate_quiz_recommendations
print("Current Working Directory:", os.getcwd())

app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.mount("/new", StaticFiles(directory="frontend"), name="frontend")
app.mount("/model-images", StaticFiles(directory="backend/HD-VITON/VITON-HD/datasets/test/image"), name="model-images")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/quiz1.html", "rb") as f:
        content = f.read().decode("utf-8", errors="replace")
    return HTMLResponse(content=content)

@app.post("/vton")
async def tryon(person_img: UploadFile = File(...), cloth_img: UploadFile = File(...)):
    person_path = f"backend/static/{person_img.filename}"
    cloth_path = f"backend/static/{cloth_img.filename}"

    with open(person_path, "wb") as buffer:
        shutil.copyfileobj(person_img.file, buffer)
    with open(cloth_path, "wb") as buffer:
        shutil.copyfileobj(cloth_img.file, buffer)

    output_path = run_vton_pipeline(person_path, cloth_path)
    return FileResponse(output_path, media_type="image/png")


@app.get("/recommend/{cloth_id}")
def recommend(cloth_id: str):
    print("it hit")
    recommendations=generate_recommendations(cloth_id)
    print(recommendations)
    return {"recommendations": recommendations}



@app.post("/stylequiz/recommend")
async def style_quiz_recommendation(request: Request):
    data = await request.json()
    recommendations = generate_quiz_recommendations(data)
    return {"recommendations": recommendations}


HD_VITON_DIR = "backend/HD-ViTON/VITON-HD"
PAIRS_FILE = os.path.join(HD_VITON_DIR, "datasets","test_pairs.txt")
@app.post("/tryon/selected")
async def run_selected_tryon(person_id: str = Form(...), cloth_id: str = Form(...)):
    try:
        # Write the selected pair to test_pairs.txt
        with open(PAIRS_FILE, "w") as f:
            f.write(f"{person_id} {cloth_id}\n")

        # Run test.py for try-on
        subprocess.run(
            [sys.executable, "test.py", "--name", "results"],
            cwd=HD_VITON_DIR,
            check=True,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "0"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Result file name format
    person_base = person_id.replace("_00.jpg", "")
    result_filename = f"{person_base}_{cloth_id}"
    result_path = os.path.join(HD_VITON_DIR, "results", "results", result_filename)

    if not os.path.exists(result_path):
        return JSONResponse(status_code=404, content={"message": f"Try-on result not found: {result_filename}"})

    return FileResponse(result_path, media_type="image/jpeg")


import glob

@app.get("/models")
def list_model_images():
    model_folder = "backend/HD-ViTON/VITON-HD/datasets/test/image"
    image_files = glob.glob(os.path.join(model_folder, "*.jpg"))
    filenames = [os.path.basename(f) for f in image_files]
    return {"models": filenames}