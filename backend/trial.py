from neo4j import GraphDatabase

def connection():
    driver=GraphDatabase.driver(uri="neo4j+s://ee387fa4.databases.neo4j.io",auth=("neo4j","oYXGQuZbCWC2VyJ65RAzSPnjq6f2WJwodZfokuEfWm8"))
    return driver

def countnode(label):
    driver_neo4j=connection()
    session=driver_neo4j.session()
    records, summary, keys = driver_neo4j.execute_query("""
    MATCH (n:Cloth) RETURN count(n)
    """,
    database_="neo4j",
    )
    for record in records:
        print(record.data())  # obtain record as dict

    # Summary information
    print("The query `{query}` returned {records_count} records in {time} ms.".format(
        query=summary.query, records_count=len(records),
        time=summary.result_available_after
    ))

countnode("lol")