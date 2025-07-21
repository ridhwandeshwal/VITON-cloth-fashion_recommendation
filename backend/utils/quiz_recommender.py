from neo4j import GraphDatabase
from collections import Counter

def connection():
    return GraphDatabase.driver(
        uri="neo4j+s://ee387fa4.databases.neo4j.io",
        auth=("neo4j", "oYXGQuZbCWC2VyJ65RAzSPnjq6f2WJwodZfokuEfWm8")
    )

# Map quiz attribute to (relationship, node label, property name)
ATTRIBUTE_MAPPING = {
    "Category": ("is_category", "Category", "name"),
    "Colour": ("is_colour", "Colour", "name"),
    "Pattern": ("has_pattern", "Pattern", "name"),
    "Material": ("of_material", "Material", "name"),
    "NeckType": ("has_necktype", "NeckType", "name"),
}

def get_matching_cloth_ids(attribute_relation, node_label, property_key, value):
    driver = connection()
    records, _, _ = driver.execute_query(
        f"""
        MATCH (n:{node_label} {{{property_key}: $value}})<-[:{attribute_relation}]-(cloth:Cloth)
        RETURN cloth.cloth_id AS id
        """,
        value=value,
        database_="neo4j"
    )
    return [row["id"] for row in records]

def generate_quiz_recommendations(quiz_data: dict) -> list[str]:
    score_counter = Counter()

    for attr, ranked_values in quiz_data.items():
        if attr not in ATTRIBUTE_MAPPING:
            continue

        relation, label, prop = ATTRIBUTE_MAPPING[attr]
        max_rank = max(ranked_values.keys())

        for rank_str, value in ranked_values.items():
            rank = int(rank_str)
            weight = int(max_rank) - rank + 1
            ids = get_matching_cloth_ids(relation, label, prop, value)
            for cloth_id in ids:
                score_counter[cloth_id] += weight

    return [cid for cid, _ in score_counter.most_common(50)]
