from models.robot_model import RobotHeartbeat
from utils.mongo_utils import robot_status

BATTERY_THRESHOLD = 60.0

async def update_robot(data: RobotHeartbeat):
    await robot_status.update_one(
        {"robot_id": data.robot_id, "map_id": data.map_id},
        {"$set": data.dict()},
        upsert=True
    )
    return {"message": "Robot status updated"}

async def get_idle_robots_by_map(map_id: str):
    robots = await robot_status.find({
        "status": {"$in": ["idle"]},
        "map_id": map_id,
        "battery_level": {"$gte": BATTERY_THRESHOLD}
    }).to_list(length=None)
    return {"robots": robots}

async def add_robot(data: RobotHeartbeat):
    existing = await robot_status.find_one({"robot_id": data.robot_id, "map_id": data.map_id})
    if existing:
        return {"error": "Robot already exists for this map"}
    await robot_status.insert_one(data.dict())
    return {"message": "Robot added successfully"}
