import os
from fastapi import APIRouter, HTTPException, Query
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

# Location model to represent x and y coordinates
class Location(BaseModel):
    x: int
    y: int

# Robot heartbeat model with valid statuses
class RobotHeartbeat(BaseModel):
    robot_id: str
    status: str  # Only "idle" or "busy" are allowed
    location: Location
    map_id: str  # Link the robot to a specific map

    # Validate status to only accept 'idle' or 'busy'
    @staticmethod
    def validate_status(status: str):
        if status not in ["idle", "busy"]:
            raise ValueError("Status must be either 'idle' or 'busy'")
        return status

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = self.validate_status(self.status)

class RobotOut(BaseModel):
    robot_id: str
    status: str
    location: Dict[str, int]
    map_id: str


# Endpoint to update robot status
@router.post("/robots/heartbeat")
async def update_robot_status(data: RobotHeartbeat):
    # Update or insert the robot status for the given map_id
    await robot_status.update_one(
        {"robot_id": data.robot_id, "map_id": data.map_id},  # include map_id in the query
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Robot status updated"}


# Endpoint to get all robots with status 'idle' or 'busy' for a specific map
@router.get("/robots/idle", response_model=Dict[str, List[RobotOut]])
async def get_idle_robots(map_id: str = Query(..., description="Map ID to filter robots")):
    # Fetch robots that are 'idle' or for the given map_id
    robots = await robot_status.find({"status": {"$in": ["idle"]}, "map_id": map_id}).to_list(length=None)
    return {"robots": robots}


# Endpoint to add a new robot
@router.post("/robots/add")
async def add_robot(data: RobotHeartbeat):
    if not data.map_id:
        raise HTTPException(status_code=400, detail="Map ID is required")
    
    existing = await robot_status.find_one({"robot_id": data.robot_id, "map_id": data.map_id})
    if existing:
        raise HTTPException(status_code=400, detail="Robot already exists for this map")
    
    # Insert the new robot with validated status
    await robot_status.insert_one(data.dict())
    return {"message": "Robot added successfully"}
