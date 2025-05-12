from pydantic import BaseModel
from typing import Dict, List

class ShelfLevelDetails(BaseModel):
    available_space: float
    sku_details: List[Dict[str, int]]

class ShelfStatusUpdate(BaseModel):
    shelf_id: str
    shelf_capacity: float
    available_space: float
    shelf_levels: Dict[str, ShelfLevelDetails]
    map_id: str
