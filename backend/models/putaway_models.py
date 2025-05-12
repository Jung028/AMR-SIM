
# models/putaway_models.py
from pydantic import BaseModel
from typing import List, Optional

class PrintInfo(BaseModel):
    type: int
    content: str

class CarrierInfo(BaseModel):
    type: int
    code: str
    name: str
    waybill_code: str

class DatesInfo(BaseModel):
    creation_date: int
    expected_finish_date: int

class OrderDetails(BaseModel):
    putaway_order_code: str
    order_type: int
    inbound_wave_code: str
    owner_code: str
    map_id: str
    print: PrintInfo
    carrier: CarrierInfo
    dates: DatesInfo
    priority: int

class SkuItem(BaseModel):
    sku_code: str
    sku_id: str
    in_batch_code: Optional[str]
    sku_level: int
    amount: int
    production_date: Optional[int]
    expiration_date: Optional[int]

class Order(BaseModel):
    order_details: OrderDetails
    sku_items: List[SkuItem]

class PutawayBody(BaseModel):
    orders: List[Order]

class PutawayHeader(BaseModel):
    warehouse_code: str
    user_id: str
    user_key: str

class PutawayRequest(BaseModel):
    header: PutawayHeader
    body: PutawayBody

class PickRequest(BaseModel):
    customer_id: str
    sku_list: list
    priority: Optional[str]

class PutawayOrderRequest(BaseModel):
    currentMapId: str
