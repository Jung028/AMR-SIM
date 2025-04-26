# services/task_service.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import os
import httpx
import random
from bson import ObjectId
from fastapi.encoders import jsonable_encoder  # Added for safe encoding

router = APIRouter()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Default to localhost if env var is not set
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

# Request model with map_id
class PutawayOrder(BaseModel):
    putaway_order_code: str
    sku_list: List[SKUItem]
    map_id: str  # Added map_id field

# Utility function to recursively convert MongoDB ObjectId to string
def serialize_dict(data):
    """Recursively convert MongoDB ObjectId to string for JSON serialization."""
    if isinstance(data, dict):
        return {k: serialize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_dict(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

# Endpoint to fetch pending putaway tasks from the database, filtered by map_id
@router.get("/task/putaway-tasks")
async def get_putaway_tasks(map_id: str):
    try:
        # Fetch tasks from the MongoDB collection for the specific map_id
        tasks = await putaway_tasks.find({"map_id": map_id}).to_list(length=100)  # Fetch up to 100 tasks
        # Convert MongoDB ObjectId to string for JSON serialization
        tasks = [serialize_dict(task) for task in tasks]
        
        return {"tasks": tasks}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching putaway tasks")

# Endpoint to generate putaway task with map_id
@router.post("/task/generate-putaway")
async def generate_putaway_task():
    try:
        async with httpx.AsyncClient() as client:

            
            # Step 1: Fetch the latest putaway order
            latest_order_response = await client.get("http://localhost:8000/orders/putaway/latest")
            latest_order_response.raise_for_status()
            latest_order_data = latest_order_response.json()

            # Go inside 'body' -> 'orders' -> first order
            order = latest_order_data.get("body", {}).get("orders", [{}])[0]

            putaway_order_code = order.get("order_details", {}).get("putaway_order_code")
            map_id = order.get("order_details", {}).get("map_id")
            sku_items = order.get("sku_items", [])

            if not putaway_order_code or not map_id or not sku_items:
                raise HTTPException(status_code=400, detail="Incomplete data in latest putaway order")

        
            # Step 2: Fetch available robots filtered by map_id
            robots_response = await client.get(f"http://localhost:8000/robots/free?map_id={map_id}")
            robots_data = robots_response.json()
            robots = robots_data.get("robots", [])
            if not robots:
                raise HTTPException(status_code=404, detail="No available robots for the given map ID")
            robot = sorted(robots, key=lambda r: r["location"]["x"])[0]

            # Step 3: Fetch available shelves filtered by map_id
            shelves_response = await client.get(f"http://localhost:8000/station/shelves?map_id={map_id}")
            shelves = shelves_response.json()
            if not shelves or not isinstance(shelves, list):
                raise HTTPException(status_code=404, detail="No available shelves for the given map ID")
            shelf = sorted(shelves, key=lambda s: s["available_space"], reverse=True)[0]

            # Step 4: Fetch available putaway stations filtered by map_id
            stations_response = await client.get(f"http://localhost:8000/station/putaway-stations?map_id={map_id}")
            stations = stations_response.json()
            if not stations or not isinstance(stations, list):
                raise HTTPException(status_code=404, detail="No available stations for the given map ID")
            station = sorted(stations, key=lambda s: s["queue_length"])[0]

        # Step 5: Prepare the task
        task = {
            "task_id": f"TASK_{random.randint(1000, 9999)}",
            "putaway_order_code": putaway_order_code,
            "robot_id": str(robot.get("robot_id")),
            "shelf_id": str(shelf.get("shelf_id")),
            "station_id": str(station.get("station_id")),
            "sku_list": sku_items,
            "map_id": map_id,
            "status": "pending"
        }

        # Insert task into MongoDB
        result = await putaway_tasks.insert_one(task)
        task["_id"] = result.inserted_id

        # Return serialized response
        serializable_task = serialize_dict(task)
        return {"message": "Putaway task created", "task": serializable_task}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")
