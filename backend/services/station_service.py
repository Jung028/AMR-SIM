import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict
from bson import ObjectId

# Load environment variables
load_dotenv()

# MongoDB connection URI
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)

# Database and collections
db_station = client["station_db"]
shelf_status = db_station["shelf_status"]
putaway_station = db_station["putaway_station"]

# FastAPI router
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

# Utility function to convert MongoDB ObjectId to string for serialization
def mongo_to_dict(mongo_obj):
    """Convert MongoDB ObjectId to string for JSON serialization."""
    if isinstance(mongo_obj, ObjectId):
        return str(mongo_obj)
    if isinstance(mongo_obj, dict):
        return {k: mongo_to_dict(v) for k, v in mongo_obj.items()}
    if isinstance(mongo_obj, list):
        return [mongo_to_dict(v) for v in mongo_obj]
    return mongo_obj

def serialize_docs(docs):
    """Apply mongo_to_dict to a list of documents."""
    return [mongo_to_dict(doc) for doc in docs]

# Endpoints

@router.post("/station/shelf/update")
async def update_shelf_status(data: ShelfStatusUpdate):
    """Update shelf status in the database."""
    try:
        await shelf_status.update_one(
            {"shelf_id": data.shelf_id},
            {"$set": data.dict()},
            upsert=True
        )
        return {"message": "Shelf status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating shelf status: {str(e)}")

@router.post("/station/load/update")
async def update_station_load(data: StationLoadUpdate):
    """Update putaway station load in the database."""
    try:
        await putaway_station.update_one(
            {"station_id": data.station_id},
            {"$set": data.dict()},
            upsert=True
        )
        return {"message": "Putaway station load updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating station load: {str(e)}")

@router.post("/station/add-shelf")
async def add_shelf(data: ShelfStatusUpdate):
    """Add a new shelf to the database."""
    try:
        existing = await shelf_status.find_one({"shelf_id": data.shelf_id})
        if existing:
            raise HTTPException(status_code=400, detail="Shelf already exists")
        
        await shelf_status.insert_one(data.dict())
        return {"message": "Shelf added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding shelf: {str(e)}")

@router.post("/station/add-putaway-station")
async def add_putaway_station(data: StationLoadUpdate):
    """Add a new putaway station to the database."""
    try:
        existing = await putaway_station.find_one({"station_id": data.station_id})
        if existing:
            raise HTTPException(status_code=400, detail="Putaway station already exists")
        
        await putaway_station.insert_one(data.dict())
        return {"message": "Putaway station added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding putaway station: {str(e)}")

@router.get("/station/shelves")
async def get_shelves():
    """Retrieve all shelves from the database."""
    try:
        shelves_cursor = shelf_status.find()
        shelves = await shelves_cursor.to_list(length=None)

        # Convert ObjectIds to strings
        shelves = serialize_docs(shelves)

        if not shelves:
            raise HTTPException(status_code=404, detail="No shelves available")
        return shelves
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shelves: {str(e)}")

@router.get("/station/putaway-stations")
async def get_putaway_stations():
    """Retrieve all putaway stations from the database."""
    try:
        stations_cursor = putaway_station.find()
        stations = await stations_cursor.to_list(length=None)

        # Convert ObjectIds to strings
        stations = serialize_docs(stations)

        if not stations:
            raise HTTPException(status_code=404, detail="No putaway stations available")
        return stations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching putaway stations: {str(e)}")
