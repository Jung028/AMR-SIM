# models/putaway_models.py
from pydantic import BaseModel
from typing import List

class SKUItem(BaseModel):
    sku_id: str
    sku_code: str
    amount: int
    sku_level: int
    in_batch_code: str
    production_date: int
    expiration_date: int

class PutawayOrder(BaseModel):
    putaway_order_code: str
    sku_list: List[SKUItem]
    map_id: str
