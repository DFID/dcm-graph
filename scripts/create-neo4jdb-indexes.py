import os
# sudo pip3 install -U python-dotenv
from dotenv import load_dotenv
from neo4j import GraphDatabase
load_dotenv()
# Prepare the bolt driver                               
uri = os.getenv("boltURL")
driver = GraphDatabase.driver(uri, auth=(os.getenv("neo4jUser"), os.getenv("neo4jPass")))

def create_index(tx):
    tx.run("create index on :Activities(ActivityIdentifier)")
    tx.run("create index on :Organisations(OrgIdentifier)")

with driver.session() as session:
    session.write_transaction(create_index)