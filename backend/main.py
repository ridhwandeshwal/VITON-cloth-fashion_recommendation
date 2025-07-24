from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import subprocess
import sys
import glob

from backend.utils.run_kaggle import run_vton_pipeline
from backend.utils.recommendation import generate_recommendations
from backend.utils.quiz_recommender import generate_quiz_recommendations

from fastapi import FastAPI, Request
from collections import Counter
from neo4j import GraphDatabase
import spacy
from spacy.matcher import Matcher


app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
app.mount("/new", StaticFiles(directory="frontend"), name="frontend")
app.mount("/model-images", StaticFiles(directory="backend/HD-VITON/VITON-HD/datasets/test/image"), name="model-images")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/style-quiz-page.html", "rb") as f:
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
    # print("it hit")
    recommendations=generate_recommendations(cloth_id)
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


STYLETRANSFERDIR="backend/neural style tranfer trial/Neural-Style-Transfer"
@app.post("/styletransfer/selected")
async def run_selected_styletransfer(person_id: str = Form(...), cloth_id: str = Form(...)):
    try:
        # Run test.py for try-on
        print("came here")
        subprocess.run(
            [sys.executable, "Main.py"],
            cwd=STYLETRANSFERDIR,
            check=True,
            env={
                **os.environ,
                "CUDA_VISIBLE_DEVICES": "0",
                "CONTENT_IMG": f"D:/trial website/frontend/cloth/{cloth_id}",
                "STYLE_IMG": f"D:/trial website/frontend/cloth/{person_id}"
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Result file name format
    result_filename = "stylized_image.jpeg"
    result_path = os.path.join(STYLETRANSFERDIR, result_filename)

    if not os.path.exists(result_path):
        return JSONResponse(status_code=404, content={"message": f"Try-on result not found: {result_filename}"})

    return FileResponse(result_path, media_type="image/jpeg")



@app.get("/models")
def list_model_images():
    model_folder = "backend/HD-ViTON/VITON-HD/datasets/test/image"
    image_files = glob.glob(os.path.join(model_folder, "*.jpg"))
    filenames = [os.path.basename(f) for f in image_files]
    return {"models": filenames}


def NER(query):
    nlp = spacy.blank("en")
    matcher = Matcher(nlp.vocab)

    colors = ["Blue", "Red", "Green", "Yellow", "Black", "White", "Teal", "Orange", "Maroon", "Purple", "Pink", "Gray"]
    patterns = ["Floral", "Striped", "Plain", "Polka", "Animal", "Graphic"]
    category = ["Top", "T-shirt", "BodySuit", "Dress", "Tank-Top", "Tube-Top"]
    material = ["Cotton", "Sequin", "Silky", "Mesh", "Synthetic"]
    brands = ["Tommy Hilfiger", "Calvin Klein", "Levis", "Polo", "Nike", "Adidas", "Superdry", "Puma", "Gap"]

    matcher.add("Color", [[{"LOWER": color.lower()}] for color in colors])
    matcher.add("Pattern", [[{"LOWER": p.lower()}] for p in patterns])
    matcher.add("Category", [[{"LOWER": c.lower()}] for c in category])
    matcher.add("Material", [[{"LOWER": m.lower()}] for m in material])
    matcher.add("Brand", [[{"LOWER": b.lower()}] for b in brands])

    doc = nlp(query.lower())
    matches = matcher(doc)
    entities= {"Color": [], "Category": [], "Pattern": [], "Material": [], "Brand": []}
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if span.text not in entities[label]:
            entities[label].append(span.text)
    print(entities)
    return entities

def connection():
    return GraphDatabase.driver(
        uri="neo4j+s://ee387fa4.databases.neo4j.io",
        auth=("neo4j", "oYXGQuZbCWC2VyJ65RAzSPnjq6f2WJwodZfokuEfWm8")
    )

RELATIONSHIP_MAP = {
    "Color": ("is_colour", "Colour", "name"),
    "Category": ("is_category", "Category", "name"),
    "Pattern": ("has_pattern", "Pattern", "name"),
    "Material": ("of_material", "Material", "name"),
    "Brand": ("of_brand", "Brand", "name"),
}

@app.post("/usersearch")
async def search_query(request: Request):
    data = await request.json()
    query = data.get("query")
    entitydict = NER(query)
    all_matches = []

    driver = connection()

    for entity_type, values in entitydict.items():
        if entity_type not in RELATIONSHIP_MAP:
            continue

        rel, label, prop = RELATIONSHIP_MAP[entity_type]

        for val in values:
            val=val[:1].upper() + val[1:]
            print(label,prop,rel,val)
            records, _, _ = driver.execute_query(
                f"""
                MATCH (n:{label} {{{prop}: $value}})<-[:{rel}]-(cloth:Cloth)
                RETURN cloth.cloth_id AS id
                """,
                value=val,
                database_="neo4j"
            )
            all_matches.extend([row["id"] for row in records])
    print(all_matches)
    counter = Counter(all_matches)
    top_50_ids = [item for item, _ in counter.most_common(50)]
    return {"recommendations": top_50_ids}



@app.post("/custom_recommend")
async def custom_recommend(request: Request):
    data = await request.json()
    
    filters = {
        "Category": data.get("Category", []),
        "Pattern": data.get("Pattern", []),
        "Colour": data.get("Colour", []),
        "Material": data.get("Material", []),
        "Occasion": data.get("Occasion", []),
        "Season": data.get("Season", []),
        "NeckType": data.get("Neckline", []),
        "SleeveLength": data.get("Sleeve", []),
    }
    # Map filter key to (relationship_type, label, property_name)
    schema_map = {
        "Category": ("is_category", "Category", "name"),
        "Pattern": ("has_pattern", "Pattern", "name"),
        "Colour": ("is_colour", "Colour", "name"),
        "Material": ("of_material", "Material", "name"),
        "Occasion": ("for_occasion", "Occasion", "name"),
        "Season": ("for_season", "Season", "name"),
        "NeckType": ("has_necktype", "Neckline", "name"),
        "SleeveLength": ("has_sleevelength", "Sleeve", "length"),
    }

    all_ids = []
    driver=connection()
    for key, values in filters.items():
        if key not in schema_map:
            continue
        rel, label, prop = schema_map[key]

        for val in values:
            print(rel,label,prop,val)
            with driver.session() as session:
                result = session.run(
                    f"""
                    MATCH (c:Cloth)-[:{rel}]->(a:{label} {{{prop}: $val}})
                    RETURN c.cloth_id AS cloth_id
                    """,
                    val=val
                )
                
                all_ids.extend([r["cloth_id"] for r in result])
    
    top_ids = [item for item, _ in Counter(all_ids).most_common(50)]
    return {"recommendations": top_ids}