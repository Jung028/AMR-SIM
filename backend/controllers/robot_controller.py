from fastapi import APIRouter, HTTPException, Query
from models.robot_model import RobotHeartbeat, RobotOut
from services.robot_service import update_robot, get_idle_robots_by_map, add_robot as add_robot_service
from typing import Dict, List

router = APIRouter()

@router.post("/robots/heartbeat")
async def update_robot_status(data: RobotHeartbeat):
    return await update_robot(data)

@router.get("/robots/idle", response_model=Dict[str, List[RobotOut]])
async def get_idle_robots(map_id: str = Query(..., description="Map ID to filter robots")):
    return await get_idle_robots_by_map(map_id)

@router.post("/robots/add")
async def add_robot(data: RobotHeartbeat):
    result = await add_robot_service(data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
