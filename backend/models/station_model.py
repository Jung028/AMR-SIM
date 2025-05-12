from pydantic import BaseModel
from typing import Dict

class StationLoadUpdate(BaseModel):
    station_id: str
    queue_length: int
    location: Dict[str, float]
    map_id: str
