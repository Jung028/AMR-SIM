from pydantic import BaseModel
from typing import List, Optional

class Component(BaseModel):
    id: str
    type: str
    row: int
    col: int

class MapRequest(BaseModel):
    name: str
    rows: int
    cols: int
    components: List[Component]

class UpdateMapRequest(BaseModel):
    name: Optional[str]
    rows: Optional[int]
    cols: Optional[int]
    components: Optional[List[Component]]
