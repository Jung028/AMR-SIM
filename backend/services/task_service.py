from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
import httpx
import random

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_task = client["task_db"]
putaway_tasks = db_task["putaway_tasks"]

class PutawayOrder(BaseModel):
    order_id: str
    sku_list: list  # e.g., [{"sku_id": "SKU123", "quantity": 2}]

@router.post("/task/generate-putaway")
async def generate_putaway_task(order: PutawayOrder):
    try:
        async with httpx.AsyncClient() as client:
            # Get robot
            robots = await client.get("http://localhost:8000/robots/free")
            robot = sorted(robots.json(), key=lambda r: r["location"]["x"])[0]

            # Get shelves
            shelves = await client.get("http://localhost:8000/station/shelves")
            shelf = sorted(shelves.json(), key=lambda s: s["available_space"], reverse=True)[0]

            # Get station
            stations = await client.get("http://localhost:8000/station/putaway-stations")
            station = sorted(stations.json(), key=lambda s: s["queue_length"])[0]

        # Prepare task
        task = {
            "task_id": f"TASK_{random.randint(1000, 9999)}",
            "order_id": order.order_id,
            "robot_id": robot["robot_id"],
            "shelf_id": shelf["shelf_id"],
            "station_id": station["station_id"],
            "sku_list": order.sku_list,
            "status": "pending"
        }

        await putaway_tasks.insert_one(task)
        return {"message": "Task created", "task": task}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
