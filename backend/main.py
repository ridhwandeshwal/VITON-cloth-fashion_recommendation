from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

from backend.utils.run_kaggle import run_vton_pipeline
from backend.utils.recommendation import generate_recommendations
from backend.utils.quiz_recommender import generate_quiz_recommendations
print("Current Working Directory:", os.getcwd())

app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.mount("/new", StaticFiles(directory="frontend"), name="frontend")
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
    return {"recommendations": generate_recommendations(cloth_id)}



@app.post("/stylequiz/recommend")
async def style_quiz_recommendation(request: Request):
    data = await request.json()
    recommendations = generate_quiz_recommendations(data)
    return {"recommendations": recommendations}
