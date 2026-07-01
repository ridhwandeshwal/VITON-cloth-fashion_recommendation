import logging

from neo4j import Driver

from backend.utils.modal_client import call_vton

logger = logging.getLogger(__name__)

CATEGORY_TO_IDM_VTON = {
    "Top": "upper_body",
    "T-shirt": "upper_body",
    "Tank-Top": "upper_body",
    "Tube-Top": "upper_body",
    "Dress": "dresses",
    "BodySuit": "dresses",
}


def describe_garment(cloth_id: str, driver: Driver, database: str | None) -> tuple[str, str]:
    """
    Build a short garment description + IDM-VTON category ("upper_body" /
    "lower_body" / "dresses") for cloth_id from the existing Neo4j graph
    (Cloth -[:is_category]-> Category, -[:is_colour]-> Colour,
    -[:of_material]-> Material — same relationships main.py already queries
    for search/recommendations).
    """
    records, _, _ = driver.execute_query(
        """
        MATCH (cloth:Cloth {cloth_id: $cloth_id})
        OPTIONAL MATCH (cloth)-[:is_category]->(cat:Category)
        OPTIONAL MATCH (cloth)-[:is_colour]->(col:Colour)
        OPTIONAL MATCH (cloth)-[:of_material]->(mat:Material)
        RETURN cat.name AS category, col.name AS colour, mat.name AS material
        LIMIT 1
        """,
        cloth_id=cloth_id,
        database_=database,
    )

    category_name = None
    words = []
    if records:
        row = records[0]
        category_name = row["category"]
        if row["colour"]:
            words.append(row["colour"])
        if row["material"]:
            words.append(row["material"])
        if category_name:
            words.append(category_name)

    description = " ".join(words).strip().lower() or "a garment"
    idm_category = CATEGORY_TO_IDM_VTON.get(category_name, "upper_body")
    return description, idm_category


async def run_vton_pipeline(
    person_bytes: bytes,
    garment_bytes: bytes,
    garment_des: str = "a garment",
    category: str = "upper_body",
) -> bytes:
    """Run virtual try-on via the Modal-hosted IDM-VTON endpoint."""
    return await call_vton(person_bytes, garment_bytes, garment_des, category)
