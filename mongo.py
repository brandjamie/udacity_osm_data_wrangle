import json

def insert_data(data, db):
    db.colchester.insert(data)

def mongo_import():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.colchester
    with open('colchester_england.osm.json') as f:
        data = json.loads(f.read())
        insert_data(data, db)


mongo_import()
