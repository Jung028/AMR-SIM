from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import os
import httpx
import random
from bson import ObjectId
from fastapi.encoders import jsonable_encoder  # ✅ Added for safe encoding

router = APIRouter()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_task = client["task_db"]
putaway_tasks = db_task["putaway_tasks"]

# SKU model
class SKUItem(BaseModel):
    sku_id: str
    sku_code: str
    amount: int
    sku_level: int
    in_batch_code: str
    production_date: int
    expiration_date: int

# Request model
class PutawayOrder(BaseModel):
    order_id: str
    sku_list: List[SKUItem]

# Convert ObjectId recursively in dict
def serialize_dict(data):
    if isinstance(data, dict):
        return {k: serialize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_dict(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

@router.post("/task/generate-putaway")
async def generate_putaway_task(order: PutawayOrder):
    try:
        async with httpx.AsyncClient() as client:
            robots_response = await client.get("http://localhost:8000/robots/free")
            robots_data = robots_response.json()
            robots = robots_data.get("robots", [])
            if not robots:
                raise HTTPException(status_code=404, detail="No available robots")
            robot = sorted(robots, key=lambda r: r["location"]["x"])[0]

            shelves_response = await client.get("http://localhost:8000/station/shelves")
            try:
                shelves = shelves_response.json()
            except ValueError:
                raise HTTPException(status_code=500, detail="Failed to parse shelves data")
            if not shelves or not isinstance(shelves, list):
                raise HTTPException(status_code=404, detail="No available shelves")
            shelf = sorted(shelves, key=lambda s: s["available_space"], reverse=True)[0]

            stations_response = await client.get("http://localhost:8000/station/putaway-stations")
            try:
                stations = stations_response.json()
            except ValueError:
                raise HTTPException(status_code=500, detail="Failed to parse putaway stations data")
            if not stations or not isinstance(stations, list):
                raise HTTPException(status_code=404, detail="No available stations")
            station = sorted(stations, key=lambda s: s["queue_length"])[0]

        # Convert IDs to strings
        robot_id = str(robot.get("robot_id"))
        shelf_id = str(shelf.get("shelf_id"))
        station_id = str(station.get("station_id"))

        task = {
            "task_id": f"TASK_{random.randint(1000, 9999)}",
            "order_id": order.order_id,
            "robot_id": robot_id,
            "shelf_id": shelf_id,
            "station_id": station_id,
            "sku_list": [sku.dict() for sku in order.sku_list],
            "status": "pending"
        }

        result = await putaway_tasks.insert_one(task)
        task["_id"] = result.inserted_id  # Add ObjectId for response

        # ✅ Convert everything to JSON-safe values
        serializable_task = serialize_dict(task)

        return {"message": "Putaway task created", "task": serializable_task}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")
