from pydantic import BaseModel
from typing import Dict

class Location(BaseModel):
    x: int
    y: int

class RobotHeartbeat(BaseModel):
    robot_id: str
    status: str
    location: Location
    map_id: str

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
