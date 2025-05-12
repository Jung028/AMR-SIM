import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)

db_station = client["station_db"]
shelf_status = db_station["shelf_status"]
putaway_station = db_station["putaway_station"]

def mongo_to_dict(mongo_obj):
    if isinstance(mongo_obj, ObjectId):
        return str(mongo_obj)
    if isinstance(mongo_obj, dict):
        return {k: mongo_to_dict(v) for k, v in mongo_obj.items()}
    if isinstance(mongo_obj, list):
        return [mongo_to_dict(v) for v in mongo_obj]
    return mongo_obj

def serialize_docs(docs):
    return [mongo_to_dict(doc) for doc in docs]


