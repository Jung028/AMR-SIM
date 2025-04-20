import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_robot = client["robot_db"]
robot_status = db_robot["robot_status"]

router = APIRouter()

# Models
class Location(BaseModel):
    x: int
    y: int

class RobotHeartbeat(BaseModel):
    robot_id: str
    status: str  # "free" or "busy"
    location: Location

class RobotOut(BaseModel):
    robot_id: str
    status: str
    location: Dict[str, int]

# Endpoint to update robot status
@router.post("/robots/heartbeat")
async def update_robot_status(data: RobotHeartbeat):
    await robot_status.update_one(
        {"robot_id": data.robot_id},
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Robot status updated"}

# Endpoint to get all free robots
@router.get("/robots/free", response_model=Dict[str, List[RobotOut]])
async def get_free_robots():
    robots = await robot_status.find({"status": "free"}).to_list(length=None)
    return {"robots": robots}


# Endpoint to add a new robot
@router.post("/robots/add")
async def add_robot(data: RobotHeartbeat):
    existing = await robot_status.find_one({"robot_id": data.robot_id})
    if existing:
        raise HTTPException(status_code=400, detail="Robot already exists")
    
    await robot_status.insert_one(data.dict())
    return {"message": "Robot added successfully"}
