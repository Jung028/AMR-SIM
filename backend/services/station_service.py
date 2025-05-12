# services/station_service.py

from utils.mongo_utils import serialize_dict, putaway_station  # Import utility functions and collections
from models.station_model import StationLoadUpdate

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
    return serialize_dict(await stations_cursor.to_list(length=None))
