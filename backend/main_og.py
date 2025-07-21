from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from backend.utils.run_kaggle import run_vton_pipeline
from collections import Counter
from neo4j import GraphDatabase


app = FastAPI()


pattern=[]
app.state.pattern=[]
app.state.colour=[]
app.state.material=[]
app.state.sleevetype=[]
app.state.sleevelength=[]
app.state.season=[]
app.state.occasion=[]
app.state.category=[]
app.state.gender=[]
app.state.brand=[]
app.state.necktype=[]
app.state.length=[]

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index.html", "r") as f:
        return f.read()

@app.post("/vton")
async def tryon(person_img: UploadFile = File(...), cloth_img: UploadFile = File(...)):
    person_path = f"backend/static/{person_img.filename}"
    cloth_path = f"backend/static/{cloth_img.filename}"

    # Save images locally
    with open(person_path, "wb") as buffer:
        shutil.copyfileobj(person_img.file, buffer)
    with open(cloth_path, "wb") as buffer:
        shutil.copyfileobj(cloth_img.file, buffer)

    # Call your Kaggle VTON + segmentation logic
    output_path = run_vton_pipeline(person_path, cloth_path)

    return FileResponse(output_path, media_type="image/png")


def connection():
    driver=GraphDatabase.driver(uri="neo4j+s://ee387fa4.databases.neo4j.io",auth=("neo4j","oYXGQuZbCWC2VyJ65RAzSPnjq6f2WJwodZfokuEfWm8"))
    return driver

@app.get("/colour/")
def getSameColour(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:is_colour]->(c:Colour)<-[:is_colour]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS colour
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.colour.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Colour":row["colour"]}for row in records ]}

@app.get("/sleevelength")
def getSameSleeveLength(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:has_sleevelength]->(c:SleeveLength)<-[:has_sleevelength]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.length AS sleevelength
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.sleevelength.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Sleeve Length":row["sleevelength"]}for row in records ]}


@app.get("/sleevetype")
def getSameSleeveType(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:has_sleevetype]->(c:SleeveType)<-[:has_sleevetype]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS sleeveType
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.sleevetype.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Sleeve Type":row["sleeveType"]}for row in records ]}

@app.get("/category")
def getSameCategory(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:is_category]->(c:Category)<-[:is_category]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS category
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.category.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Category":row["category"]}for row in records ]}


@app.get("/brand")
def getSameBrand(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:of_brand]->(c:Brand)<-[:of_brand]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS brand
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.brand.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Brand":row["brand"]}for row in records ]}


@app.get("/material")
def getSameMaterial(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:of_material]->(c:Material)<-[:of_material]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS material
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.material.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Material":row["material"]}for row in records ]}

@app.get("/pattern")
def getPattern(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
MATCH (target:Cloth {cloth_id:$cloth_id})-[:has_pattern]->(c:Pattern)<-[:has_pattern]-(similar:Cloth)
WHERE similar.cloth_id <> $cloth_id
RETURN similar.cloth_id AS similar_cloth_id, c.name AS pattern
""",
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.pattern.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Pattern":row["pattern"]}for row in records ]}




@app.get("/gender")
def getsamegender(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (target:Cloth {cloth_id:$cloth_id})-[:for_gender]->(c:Gender)<-[:for_gender]-(similar:Cloth)
    WHERE similar.cloth_id <> $cloth_id
    RETURN similar.cloth_id AS similar_cloth_id, c.name AS gender
    """,
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.gender.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Gender":row["gender"]}for row in records ]}


@app.get("/occasion")
def getsameoccasion(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (target:Cloth {cloth_id:$cloth_id})-[:for_occasion]->(c:Occasion)<-[:for_occasion]-(similar:Cloth)
    WHERE similar.cloth_id <> $cloth_id
    RETURN similar.cloth_id AS similar_cloth_id, c.name AS occasion
    """,
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.occasion.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Occasion":row["occasion"]}for row in records ]}

@app.get("/season")
def getsameseason(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (target:Cloth {cloth_id:$cloth_id})-[:for_season]->(c:Season)<-[:for_season]-(similar:Cloth)
    WHERE similar.cloth_id <> $cloth_id
    RETURN similar.cloth_id AS similar_cloth_id, c.name AS season
    """,
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.season.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Season":row["season"]}for row in records ]}

@app.get("/length")
def getsamelength(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (target:Cloth {cloth_id:$cloth_id})-[:has_length]->(c:Length)<-[:has_length]-(similar:Cloth)
    WHERE similar.cloth_id <> $cloth_id
    RETURN similar.cloth_id AS similar_cloth_id, c.length AS name
    """,
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.length.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "Length":row["name"]}for row in records ]}

@app.get("/necktype")
def getsamenecktype(cloth_id):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (target:Cloth {cloth_id:$cloth_id})-[:has_necktype]->(c:NeckType)<-[:has_necktype]-(similar:Cloth)
    WHERE similar.cloth_id <> $cloth_id
    RETURN similar.cloth_id AS similar_cloth_id, c.name AS necktype
    """,
    cloth_id=cloth_id,
    database_="neo4j",
    )
    for row in records:
        app.state.necktype.append(row["similar_cloth_id"])
    return {"response": [{f"Cloth_id":row["similar_cloth_id"], "NeckType":row["necktype"]}for row in records]}

@app.post("/userlogin")
async def countnode(request: Request):
    data = await request.json()   # receive JSON body as dict
    username = data.get('username')
    driver_neo4j=connection()
    session=driver_neo4j.session()
    summary = driver_neo4j.execute_query("""
    CREATE(:User{user_id:$user_id})
    """,user_id=username,
    database_="neo4j",
    ).summary
    return {"message":"Node Created: " + username}


# final_list=app.state.pattern+app.state.colour+app.state.material+app.state.sleevetype+app.state.sleevelength+app.state.season+app.state.occasion+app.state.category+app.state.gender+app.state.brand+app.state.necktype+app.state.length

# hashmap=Counter(final_list)

@app.get("/recommend/{cloth_id}")
def get_recommendations(cloth_id: str):
    from collections import Counter

    # Reset lists
    app.state.pattern.clear()
    app.state.colour.clear()
    app.state.material.clear()
    app.state.sleevetype.clear()
    app.state.sleevelength.clear()
    app.state.season.clear()
    app.state.occasion.clear()
    app.state.category.clear()
    app.state.gender.clear()
    app.state.brand.clear()
    app.state.necktype.clear()
    app.state.length.clear()

    # Call all attribute match APIs to populate the app.state lists
    getPattern(cloth_id)
    getSameColour(cloth_id)
    getSameMaterial(cloth_id)
    getSameSleeveType(cloth_id)
    getSameSleeveLength(cloth_id)
    getsameseason(cloth_id)
    getsameoccasion(cloth_id)
    getSameCategory(cloth_id)
    getsamegender(cloth_id)
    getSameBrand(cloth_id)
    getsamenecktype(cloth_id)
    getsamelength(cloth_id)

    # Combine all results
    final_list = (
        app.state.pattern + app.state.colour + app.state.material + 
        app.state.sleevetype + app.state.sleevelength + app.state.season + 
        app.state.occasion + app.state.category + app.state.gender + 
        app.state.brand + app.state.necktype + app.state.length
    )

    # Count and get top 50
    hashmap = Counter(final_list)
    top_50 = [cloth_id for cloth_id, _ in hashmap.most_common(50)]

    return {"recommendations": top_50}

