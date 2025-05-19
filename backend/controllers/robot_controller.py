# controllers/robot_controller.py

from models.robot_model import RobotHeartbeat, RobotOut, RobotMetrics
from services.robot_service import (
    update_robot,
    get_idle_robots_by_map,
    add_robot as add_robot_service,
    log_robot_metrics,
)
from utils.mongo_utils import robot_metrics
from fastapi import APIRouter, HTTPException, Query
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

@router.post("/robots/metrics")
async def submit_robot_metrics(data: RobotMetrics):
    return await log_robot_metrics(data)


@router.post("/robot_metrics/add")
async def add_robot_metric(metric: RobotMetrics):
    data = metric.dict()
    await robot_metrics.insert_one(data)
    return {"message": "Robot metrics recorded successfully."}


@router.get("/robots/status/by-map/{map_id}", response_model=Dict[str, List[RobotOut]])
async def get_robot_status_by_map(map_id: str):
    robots = await get_idle_robots_by_map(map_id)
    if robots is None:
        raise HTTPException(status_code=404, detail="No robots found for the given map ID")
    return robots
