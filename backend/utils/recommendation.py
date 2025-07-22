from neo4j import GraphDatabase
from collections import Counter

def connection():
    return GraphDatabase.driver(
        uri="neo4j+s://ee387fa4.databases.neo4j.io",
        auth=("neo4j", "oYXGQuZbCWC2VyJ65RAzSPnjq6f2WJwodZfokuEfWm8")
    )

def get_similar_clothes(cloth_id: str, relationship: str, label: str, attr_name: str) -> list[str]:
    driver_neo4j = connection()
    records, _, _ = driver_neo4j.execute_query(f"""
        MATCH (target:Cloth {{cloth_id: $cloth_id}})-[:{relationship}]->(c:{label})<-[:{relationship}]-(similar:Cloth)
        WHERE similar.cloth_id <> $cloth_id
        RETURN similar.cloth_id AS id
    """, cloth_id=cloth_id, database_="neo4j")
    return [row["id"] for row in records]

def     generate_recommendations(cloth_id: str) -> list[str]:
    attributes = [
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

    all_matches = []
    for rel, label, attr in attributes:
        matches = get_similar_clothes(cloth_id, rel, label, attr)
        all_matches.extend(matches)

    score_map = Counter(all_matches)
    top_ids = [cloth for cloth, _ in score_map.most_common(50)]
    return top_ids
