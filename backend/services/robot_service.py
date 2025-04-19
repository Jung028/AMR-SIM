# backend/services/robot_service.py

import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_robot = client["robot_db"]

robot_status = db_robot["robot_status"]

router = APIRouter()

# Models
class RobotHeartbeat(BaseModel):
    robot_id: str
    status: str  # "free" or "busy"
    location: dict  # e.g., {"x": 5, "y": 3}

# Endpoints
@router.post("/robots/heartbeat")
async def update_robot_status(data: RobotHeartbeat):
    await robot_status.update_one(
        {"robot_id": data.robot_id},
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Robot status updated"}
