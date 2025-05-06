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





@router.post("/task/generate-putaway")
async def generate_putaway_task():
    MAX_TASKS_PER_ROBOT = 3  # Limit of tasks per robot

    try:
        async with httpx.AsyncClient() as client:
            print("Fetching latest putaway order...")
            latest_order_response = await client.get("http://localhost:8000/orders/putaway/latest")
            latest_order_response.raise_for_status()
            latest_order_data = latest_order_response.json()
            order = latest_order_data.get("body", {}).get("orders", [{}])[0]

            print(f"Latest order: {order}")
            putaway_order_code = order.get("order_details", {}).get("putaway_order_code")
            map_id = order.get("order_details", {}).get("map_id")
            sku_items = order.get("sku_items", [])

            if not putaway_order_code or not map_id or not sku_items:
                raise HTTPException(status_code=400, detail="Incomplete data in latest putaway order")

            print("Fetching available robots...")
            robots_response = await client.get(f"http://localhost:8000/robots/idle?map_id={map_id}")
            robots_response.raise_for_status()
            robots_data = robots_response.json()
            robots = robots_data.get("robots", [])
            if not robots:
                raise HTTPException(status_code=404, detail="No available robots")

            # Initialize robot task tracking
            robot_task_counts = {robot["robot_id"]: 0 for robot in robots}
            sorted_robots = sorted(robots, key=lambda r: r["location"]["x"])  # Sort by location
            robot_index = 0

            print("Fetching available shelves...")
            shelves_response = await client.get(f"http://localhost:8000/station/shelves?map_id={map_id}")
            shelves_response.raise_for_status()
            shelves = shelves_response.json()
            if not shelves:
                raise HTTPException(status_code=404, detail="No shelves found")

            print("Fetching SKU packing info...")
            sku_dimensions = {}
            for sku in sku_items:
                sku_id = sku["sku_id"]
                print(f"Fetching SKU info for {sku_id}...")
                sku_info_response = await client.get(f"http://localhost:8000/get-sku/{sku_id}")
                sku_info_response.raise_for_status()
                sku_info_data = sku_info_response.json()
                packing_info = sku_info_data["sku_data"].get("sku_packing", [])
                if not packing_info:
                    raise HTTPException(status_code=400, detail=f"SKU {sku_id} has no packing data")
                primary = packing_info[0].get("primary")
                if not primary:
                    raise HTTPException(status_code=400, detail=f"SKU {sku_id} lacks primary packing")

                sku_dimensions[sku_id] = {
                    "volume": primary.get("sku_packing_volume", 0.0),
                    "height": primary.get("sku_packing_height", 0.0)
                }

            putaway_tasks_created = []

            for sku in sku_items:
                sku_id = sku["sku_id"]
                total_amount = sku["amount"]
                volume_per_unit = sku_dimensions[sku_id]["volume"]
                height = sku_dimensions[sku_id]["height"]
                amount_remaining = total_amount

                for shelf in sorted(shelves, key=lambda s: s["available_space"], reverse=True):
                    if amount_remaining <= 0:
                        break

                    for level_name in ["third", "second", "ground"]:
                        level = shelf["shelf_levels"].get(level_name)
                        if not level:
                            continue
                        level_height = level.get("max_height", float('inf'))
                        if height > level_height:
                            continue

                        max_units_fit = int(level["available_space"] // volume_per_unit)
                        units_to_place = min(amount_remaining, max_units_fit)

                        if units_to_place > 0:
                            used_volume = units_to_place * volume_per_unit
                            level["available_space"] -= used_volume
                            level.setdefault("sku_details", []).append({
                                "sku_id": sku_id,
                                "amount": units_to_place
                            })
                            shelf["available_space"] -= used_volume

                            print("Assigning station for task...")
                            stations_response = await client.get(f"http://localhost:8000/station/putaway-stations?map_id={map_id}")
                            stations_response.raise_for_status()
                            stations = stations_response.json()
                            if not stations:
                                raise HTTPException(status_code=404, detail="No stations found")
                            station = sorted(stations, key=lambda s: s["queue_length"])[0]

                            # Assign robot that hasn't reached task limit
                            assigned_robot = None
                            for _ in range(len(sorted_robots)):
                                current_robot = sorted_robots[robot_index]
                                robot_id = current_robot["robot_id"]

                                if robot_task_counts[robot_id] < MAX_TASKS_PER_ROBOT:
                                    assigned_robot = current_robot
                                    robot_task_counts[robot_id] += 1
                                    break
                                else:
                                    robot_index = (robot_index + 1) % len(sorted_robots)

                            if not assigned_robot:
                                raise HTTPException(status_code=500, detail="Not enough robot capacity to assign all tasks")

                            task = {
                                "task_id": f"TASK_{random.randint(1000, 9999)}",
                                "putaway_order_code": putaway_order_code,
                                "robot_id": str(assigned_robot.get("robot_id")),
                                "station_id": station.get("station_id"),
                                "map_id": map_id,
                                "shelf_id": shelf.get("shelf_id"),
                                "level": level_name,
                                "sku_id": sku_id,
                                "amount": units_to_place,
                                "status": "pending"
                            }
                            putaway_tasks_created.append(task)
                            amount_remaining -= units_to_place
                            break

                if amount_remaining > 0:
                    raise HTTPException(status_code=400, detail=f"Not enough space for SKU {sku_id}, {amount_remaining} left")

        print("Saving tasks to DB...")
        response_tasks = []
        for task in putaway_tasks_created:
            result = await putaway_tasks.insert_one(task)
            task["_id"] = str(result.inserted_id)

            filtered_task = {
                "_id": task["_id"],
                "task_id": task["task_id"],
                "putaway_order_code": task["putaway_order_code"],
                "robot_id": task["robot_id"],
                "station_id": task["station_id"],
                "map_id": task["map_id"],
                "shelf_id": task["shelf_id"],
                "level": task["level"],
                "sku_id": task["sku_id"],
                "amount": task["amount"],
                "status": task["status"]
            }
            response_tasks.append(filtered_task)
            print(f"Inserted task: {task['task_id']}")

        return {"message": "Putaway tasks created", "tasks": response_tasks}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")
