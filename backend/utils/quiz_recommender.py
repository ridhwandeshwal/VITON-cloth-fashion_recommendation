from collections import Counter

from neo4j import Driver

from backend.utils.db import get_database, get_driver

# Map quiz attribute to (relationship, node label, property name)
ATTRIBUTE_MAPPING = {
    "Category": ("is_category", "Category", "name"),
    "Colour": ("is_colour", "Colour", "name"),
    "Pattern": ("has_pattern", "Pattern", "name"),
    "Material": ("of_material", "Material", "name"),
    "NeckType": ("has_necktype", "NeckType", "name"),
}


def get_matching_cloth_ids(
    driver: Driver, attribute_relation: str, node_label: str, property_key: str, value
) -> list[str]:
    records, _, _ = driver.execute_query(
        f"""
        MATCH (n:{node_label} {{{property_key}: $value}})<-[:{attribute_relation}]-(cloth:Cloth)
        RETURN cloth.cloth_id AS id
        """,
        value=value,
        database_=get_database(),
    )
    return [row["id"] for row in records]


def generate_quiz_recommendations(quiz_data: dict, driver: Driver | None = None) -> list[str]:
    driver = driver or get_driver()
    score_counter: Counter = Counter()

    for attr, ranked_values in quiz_data.items():
        if attr not in ATTRIBUTE_MAPPING:
            continue

        relation, label, prop = ATTRIBUTE_MAPPING[attr]
        max_rank = max(ranked_values.keys())

        for rank_str, value in ranked_values.items():
            rank = int(rank_str)
            weight = int(max_rank) - rank + 1
            ids = get_matching_cloth_ids(driver, relation, label, prop, value)
            for cloth_id in ids:
                score_counter[cloth_id] += weight

    return [cid for cid, _ in score_counter.most_common(50)]
