# backend/services/station_service.py

import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_station = client["station_db"]

shelf_status = db_station["shelf_status"]
putaway_station = db_station["putaway_station"]

router = APIRouter()

# Models
class ShelfStatusUpdate(BaseModel):
    shelf_id: str
    available_space: int
    sku_group: str

class StationLoadUpdate(BaseModel):
    station_id: str
    queue_length: int
    location: Dict[str, float]

# Endpoints
@router.post("/station/shelf/update")
async def update_shelf_status(data: ShelfStatusUpdate):
    await shelf_status.update_one(
        {"shelf_id": data.shelf_id},
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Shelf status updated"}

@router.post("/station/load/update")
async def update_station_load(data: StationLoadUpdate):
    await putaway_station.update_one(
        {"station_id": data.station_id},
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Putaway station load updated"}
