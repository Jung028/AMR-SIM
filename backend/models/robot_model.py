# models/robot_model.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

class Location(BaseModel):
    x: int
    y: int

class RobotHeartbeat(BaseModel):
    robot_id: str
    status: str
    location: Location
    map_id: str
    battery_level: float = Field(..., ge=0, le=100)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # Add this

    @staticmethod
    def validate_status(status: str):
        if status not in ["idle", "busy", "moving", "charging"]:
            raise ValueError("Status must be 'idle', 'busy', 'moving', or 'charging'")
        return status

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = self.validate_status(self.status)

class RobotOut(BaseModel):
    robot_id: str
    status: str
    location: Dict[str, int]
    map_id: str
    battery_level: float

class RobotMetrics(BaseModel):
    robot_id: str
    task_id: str
    task_start_time: datetime
    task_end_time: datetime
    battery_start_level: float = Field(..., ge=0, le=100)
    battery_end_level: float = Field(..., ge=0, le=100)
    task_duration: Optional[float] = None  # Can be calculated
    distance: Optional[float] = None
    errors: Optional[List[str]] = []
    map_id: str
