from utils.mongo_utils import putaway_station
from bson import ObjectId
from models.station_model import StationLoadUpdate

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

async def update_station(data: StationLoadUpdate):
    return await putaway_station.update_one(
        {"station_id": data.station_id, "map_id": data.map_id},
        {"$set": data.dict()},
        upsert=True
    )

async def add_station(data: StationLoadUpdate):
    existing = await putaway_station.find_one({"station_id": data.station_id, "map_id": data.map_id})
    if existing:
        return False
    await putaway_station.insert_one(data.dict())
    return True

async def get_stations():
    stations_cursor = putaway_station.find()
    return serialize_docs(await stations_cursor.to_list(length=None))
