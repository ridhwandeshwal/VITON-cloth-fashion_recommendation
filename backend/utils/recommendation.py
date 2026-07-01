from collections import Counter

from neo4j import Driver

from backend.utils.db import get_database, get_driver

ATTRIBUTES = [
    ("is_colour", "Colour", "name"),
    ("has_pattern", "Pattern", "name"),
    ("of_material", "Material", "name"),
    ("has_sleevetype", "SleeveType", "name"),
    ("has_sleevelength", "SleeveLength", "length"),
    ("for_season", "Season", "name"),
    ("for_occasion", "Occasion", "name"),
    ("is_category", "Category", "name"),
    ("for_gender", "Gender", "name"),
    ("of_brand", "Brand", "name"),
    ("has_necktype", "NeckType", "name"),
    ("has_length", "Length", "length"),
]


def get_similar_clothes(
    driver: Driver, cloth_id: str, relationship: str, label: str
) -> list[str]:
    records, _, _ = driver.execute_query(
        f"""
        MATCH (target:Cloth {{cloth_id: $cloth_id}})-[:{relationship}]->(c:{label})<-[:{relationship}]-(similar:Cloth)
        WHERE similar.cloth_id <> $cloth_id
        RETURN similar.cloth_id AS id
        """,
        cloth_id=cloth_id,
        database_=get_database(),
    )
    return [row["id"] for row in records]


def generate_recommendations(cloth_id: str, driver: Driver | None = None) -> list[str]:
    driver = driver or get_driver()

    all_matches = []
    for rel, label, _attr in ATTRIBUTES:
        all_matches.extend(get_similar_clothes(driver, cloth_id, rel, label))

    score_map = Counter(all_matches)
    return [cloth for cloth, _ in score_map.most_common(50)]
