import os
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional

# Models
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

# FastAPI router
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_order = client["order_db"]

# Collections
putaway_orders = db_order["putaway_order_tracking"]
customer_orders = db_order["customer_orders"]
container_tracking = db_order["container_tracking"]

router = APIRouter()

# Endpoints
@router.post("/orders/putaway")
async def create_putaway_order(data: PutawayRequest):
    order_dict = data.dict()  # Convert the data to a dictionary
    await putaway_orders.insert_one(order_dict)  # Insert the order into MongoDB
    putaway_order_code = order_dict["body"]["orders"][0]["order_details"]["putaway_order_code"]
    return {
        "message": "Putaway order created",
        "putaway_order_code": putaway_order_code
    }

@router.get("/orders/putaway/{order_id}")
async def get_putaway_status(order_id: str):
    order = await putaway_orders.find_one({"header": {"order_id": order_id}})
    if not order:
        raise HTTPException(status_code=404, detail="Putaway order not found")
    order["_id"] = str(order["_id"])
    return order

@router.post("/orders/pick")
async def create_pick_order(data: PickRequest):
    await customer_orders.insert_one(data.dict())
    return {"message": "Pick order received"}
