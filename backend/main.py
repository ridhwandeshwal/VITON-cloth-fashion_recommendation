import glob
import logging
import os
from collections import Counter
from contextlib import asynccontextmanager

import httpx
import spacy
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from spacy.matcher import Matcher

from backend.utils.db import close_driver, get_database, get_driver
from backend.utils.modal_client import ModalNotConfiguredError, call_style_transfer
from backend.utils.quiz_recommender import generate_quiz_recommendations
from backend.utils.recommendation import generate_recommendations
from backend.utils.run_kaggle import describe_garment, run_vton_pipeline

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

HD_VITON_DIR = os.environ.get("HD_VITON_DIR", "backend/HD-ViTON/VITON-HD")
MODEL_IMAGE_DIR = os.path.join(HD_VITON_DIR, "datasets", "test", "image")
CLOTH_DIR = "frontend/cloth"


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()
    logger.info("Neo4j driver initialized")
    yield
    close_driver()
    logger.info("Neo4j driver closed")


app = FastAPI(lifespan=lifespan)

cors_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def revalidate_static_assets(request, call_next):
    """Serve the frontend with `Cache-Control: no-cache` so browsers always
    revalidate against the server's ETag. Without this, updated HTML/CSS can
    load while a stale cached JS keeps running (buttons render but their
    handlers are the old ones). Assets are still cached; they just can't be
    used without a quick 304 check, so deploys take effect immediately."""
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.startswith("/new"):
        response.headers["Cache-Control"] = "no-cache"
    return response


app.mount("/new", StaticFiles(directory="frontend"), name="frontend")
app.mount("/model-images", StaticFiles(directory=MODEL_IMAGE_DIR), name="model-images")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/style-quiz-page.html", "rb") as f:
        content = f.read().decode("utf-8", errors="replace")
    return HTMLResponse(content=content)


@app.get("/healthz")
def healthz():
    """Liveness probe for reverse proxies / process managers. Deliberately
    does not touch Neo4j or Modal so it stays fast and independent of them."""
    return {"status": "ok"}


@app.post("/vton")
async def tryon(person_img: UploadFile = File(...), cloth_id: str = Form(...)):
    """Try-on for an arbitrary uploaded/captured person photo (IDM-VTON needs
    no precomputed data, so this works the same as /tryon/selected — the
    garment is still looked up by id, only the person photo is uploaded)."""
    cloth_path = os.path.join(CLOTH_DIR, cloth_id)
    if not os.path.exists(cloth_path):
        raise HTTPException(status_code=404, detail=f"Cloth image not found: {cloth_id}")

    person_bytes = await person_img.read()
    with open(cloth_path, "rb") as f:
        cloth_bytes = f.read()

    driver = get_driver()
    garment_des, category = describe_garment(cloth_id, driver, get_database())

    try:
        result = await run_vton_pipeline(person_bytes, cloth_bytes, garment_des, category)
    except ModalNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except httpx.HTTPStatusError as e:
        logger.exception("Modal try-on call failed")
        raise HTTPException(status_code=502, detail=f"Try-on pipeline failed: {e}")

    return Response(content=result, media_type="image/png")


@app.get("/recommend/{cloth_id}")
def recommend(cloth_id: str):
    return {"recommendations": generate_recommendations(cloth_id)}


@app.post("/stylequiz/recommend")
async def style_quiz_recommendation(data: dict):
    return {"recommendations": generate_quiz_recommendations(data)}


# Popular preset used to seed recommendations for users who skip the cold-start
# quiz. Ranks follow the quiz semantics (rank 1 = highest weight). Colour is
# left out on purpose: weighting any single colour makes the top results
# collapse to that colour, so we let category/pattern/material drive a naturally
# mixed-colour spread.
DEFAULT_QUIZ_PROFILE = {
    "Category": {"1": "Dress", "2": "T-shirt", "3": "Top"},
    "Pattern": {"1": "Floral", "2": "Plain", "3": "Striped"},
    "Material": {"1": "Cotton", "2": "Silky", "3": "Sequin"},
}


@app.get("/stylequiz/default")
def style_quiz_default():
    """Default recommendations for visitors who skip the style quiz. Uses a
    popular preset profile so the home page is never empty, and falls back to a
    sample of the catalog if the graph yields nothing (e.g. Neo4j unavailable)."""
    try:
        recs = generate_quiz_recommendations(DEFAULT_QUIZ_PROFILE)
    except Exception:
        logger.exception("Default quiz recommendation failed; falling back to catalog sample")
        recs = []
    if not recs:
        cloth_files = sorted(glob.glob(os.path.join(CLOTH_DIR, "*.jpg")))
        recs = [os.path.basename(f) for f in cloth_files[:50]]
    return {"recommendations": recs}


@app.post("/tryon/selected")
async def run_selected_tryon(person_id: str = Form(...), cloth_id: str = Form(...)):
    person_path = os.path.join(MODEL_IMAGE_DIR, person_id)
    cloth_path = os.path.join(CLOTH_DIR, cloth_id)

    if not os.path.exists(person_path):
        raise HTTPException(status_code=404, detail=f"Model image not found: {person_id}")
    if not os.path.exists(cloth_path):
        raise HTTPException(status_code=404, detail=f"Cloth image not found: {cloth_id}")

    with open(person_path, "rb") as f:
        person_bytes = f.read()
    with open(cloth_path, "rb") as f:
        cloth_bytes = f.read()

    driver = get_driver()
    garment_des, category = describe_garment(cloth_id, driver, get_database())

    try:
        result = await run_vton_pipeline(person_bytes, cloth_bytes, garment_des, category)
    except ModalNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except httpx.HTTPStatusError as e:
        logger.exception("Modal try-on call failed")
        raise HTTPException(status_code=502, detail=f"Try-on pipeline failed: {e}")

    return Response(content=result, media_type="image/png")


@app.post("/styletransfer/selected")
async def run_selected_styletransfer(content_id: str = Form(...), style_id: str = Form(...)):
    """Neural style transfer blends two garments: the garment currently being
    viewed (content) with another garment chosen as the style reference. Both
    images come from the cloth catalog."""
    content_path = os.path.join(CLOTH_DIR, content_id)
    style_path = os.path.join(CLOTH_DIR, style_id)

    if not os.path.exists(content_path):
        raise HTTPException(status_code=404, detail=f"Cloth image not found: {content_id}")
    if not os.path.exists(style_path):
        raise HTTPException(status_code=404, detail=f"Cloth image not found: {style_id}")

    with open(content_path, "rb") as f:
        content_bytes = f.read()
    with open(style_path, "rb") as f:
        style_bytes = f.read()

    try:
        result = await call_style_transfer(content_bytes, style_bytes)
    except ModalNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except httpx.HTTPStatusError as e:
        logger.exception("Modal style transfer call failed")
        raise HTTPException(status_code=502, detail=f"Style transfer failed: {e}")

    return Response(content=result, media_type="image/jpeg")


@app.get("/models")
def list_model_images():
    image_files = glob.glob(os.path.join(MODEL_IMAGE_DIR, "*.jpg"))
    return {"models": [os.path.basename(f) for f in image_files]}


@app.get("/cloths")
def list_cloth_images():
    """Sample of the garment catalog, used as style references for neural
    style transfer."""
    image_files = sorted(glob.glob(os.path.join(CLOTH_DIR, "*.jpg")))
    return {"cloths": [os.path.basename(f) for f in image_files[:60]]}


COLORS = ["Blue", "Red", "Green", "Yellow", "Black", "White", "Teal", "Orange", "Maroon", "Purple", "Pink", "Gray"]
PATTERNS = ["Floral", "Striped", "Plain", "Polka", "Animal", "Graphic"]
CATEGORIES = ["Top", "T-shirt", "BodySuit", "Dress", "Tank-Top", "Tube-Top"]
MATERIALS = ["Cotton", "Sequin", "Silky", "Mesh", "Synthetic"]
BRANDS = ["Tommy Hilfiger", "Calvin Klein", "Levis", "Polo", "Nike", "Adidas", "Superdry", "Puma", "Gap"]

_nlp = spacy.blank("en")
_matcher = Matcher(_nlp.vocab)
_matcher.add("Color", [[{"LOWER": c.lower()}] for c in COLORS])
_matcher.add("Pattern", [[{"LOWER": p.lower()}] for p in PATTERNS])
_matcher.add("Category", [[{"LOWER": c.lower()}] for c in CATEGORIES])
_matcher.add("Material", [[{"LOWER": m.lower()}] for m in MATERIALS])
_matcher.add("Brand", [[{"LOWER": b.lower()}] for b in BRANDS])


def NER(query: str) -> dict[str, list[str]]:
    doc = _nlp(query.lower())
    matches = _matcher(doc)
    entities: dict[str, list[str]] = {"Color": [], "Category": [], "Pattern": [], "Material": [], "Brand": []}
    for match_id, start, end in matches:
        label = _nlp.vocab.strings[match_id]
        span = doc[start:end]
        if span.text not in entities[label]:
            entities[label].append(span.text)
    return entities


RELATIONSHIP_MAP = {
    "Color": ("is_colour", "Colour", "name"),
    "Category": ("is_category", "Category", "name"),
    "Pattern": ("has_pattern", "Pattern", "name"),
    "Material": ("of_material", "Material", "name"),
    "Brand": ("of_brand", "Brand", "name"),
}


class SearchRequest(BaseModel):
    query: str


@app.post("/usersearch")
async def search_query(request: SearchRequest):
    entitydict = NER(request.query)
    all_matches = []
    driver = get_driver()

    for entity_type, values in entitydict.items():
        if entity_type not in RELATIONSHIP_MAP:
            continue

        rel, label, prop = RELATIONSHIP_MAP[entity_type]

        for val in values:
            val = val[:1].upper() + val[1:]
            records, _, _ = driver.execute_query(
                f"""
                MATCH (n:{label} {{{prop}: $value}})<-[:{rel}]-(cloth:Cloth)
                RETURN cloth.cloth_id AS id
                """,
                value=val,
                database_=get_database(),
            )
            all_matches.extend([row["id"] for row in records])

    counter = Counter(all_matches)
    top_50_ids = [item for item, _ in counter.most_common(50)]
    return {"recommendations": top_50_ids}


class CustomRecommendRequest(BaseModel):
    Category: list[str] = []
    Pattern: list[str] = []
    Colour: list[str] = []
    Material: list[str] = []
    Occasion: list[str] = []
    Season: list[str] = []
    Neckline: list[str] = []
    Sleeve: list[str] = []


@app.post("/custom_recommend")
async def custom_recommend(filters: CustomRecommendRequest):
    schema_map = {
        "Category": ("is_category", "Category", "name"),
        "Pattern": ("has_pattern", "Pattern", "name"),
        "Colour": ("is_colour", "Colour", "name"),
        "Material": ("of_material", "Material", "name"),
        "Occasion": ("for_occasion", "Occasion", "name"),
        "Season": ("for_season", "Season", "name"),
        "Neckline": ("has_necktype", "Neckline", "name"),
        "Sleeve": ("has_sleevelength", "Sleeve", "length"),
    }

    all_ids = []
    driver = get_driver()
    for key, values in filters.model_dump().items():
        if key not in schema_map or not values:
            continue
        rel, label, prop = schema_map[key]

        for val in values:
            records, _, _ = driver.execute_query(
                f"""
                MATCH (c:Cloth)-[:{rel}]->(a:{label} {{{prop}: $val}})
                RETURN c.cloth_id AS cloth_id
                """,
                val=val,
                database_=get_database(),
            )
            all_ids.extend([r["cloth_id"] for r in records])

    top_ids = [item for item, _ in Counter(all_ids).most_common(50)]
    return {"recommendations": top_ids}
