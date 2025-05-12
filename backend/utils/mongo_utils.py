# utils/mongo_utils.py

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)

# Database references
db_station = client["station_db"]
shelf_status = db_station["shelf_status"]
putaway_station = db_station["putaway_station"]

db_task = client["task_db"]
putaway_tasks = db_task["putaway_tasks"]

# Utility function for ObjectId conversion
def mongo_to_dict(mongo_obj):
    if isinstance(mongo_obj, ObjectId):
        return str(mongo_obj)
    if isinstance(mongo_obj, dict):
        return {k: mongo_to_dict(v) for k, v in mongo_obj.items()}
    if isinstance(mongo_obj, list):
        return [mongo_to_dict(v) for v in mongo_obj]
    return mongo_obj

# Utility function to serialize MongoDB documents
def serialize_docs(docs):
    return [mongo_to_dict(doc) for doc in docs]

# Serialize any dictionary or list that contains ObjectIds
def serialize_dict(data):
    if isinstance(data, dict):
        return {k: serialize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_dict(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data
