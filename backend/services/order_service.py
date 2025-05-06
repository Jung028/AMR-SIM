import os
import random
import time
from fastapi import APIRouter, HTTPException
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

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

# Simulation parameters
orders_per_hour = 5
average_skus_per_order = 5
working_hours = 9
sku_per_hour_per_station = 14.5
average_number_of_skus_per_order = 5

# Generate random data for putaway order
# Fetch available sku_ids from the /get-all-skus endpoint
import httpx
from fastapi import HTTPException

async def fetch_available_skus():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/get-all-skus")
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error fetching SKUs")

            data = response.json()
            sku_ids = []

            for sku_entry in data.get("skus", []):
                header = sku_entry.get("header", {})
                warehouse_code = header.get("warehouse_code", "N/A")
                user_id = header.get("user_id", "N/A")

                sku_list = sku_entry.get("body", {}).get("sku_list", [])
                for sku in sku_list:
                    sku_id = sku.get("sku_id")
                    if sku_id:
                        print(f"[DEBUG] sku_id: {sku_id} | warehouse_code: {warehouse_code} | user_id: {user_id}")
                        sku_ids.append(sku_id)

            return sku_ids

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SKUs: {str(e)}")

# Generate random data for putaway order
async def generate_putaway_order(currentMapId):
    # Fetch available sku_ids from the external endpoint
    sku_ids = await fetch_available_skus()
    
    if not sku_ids:
        raise HTTPException(status_code=404, detail="No available SKUs found")

    # Generate SKU items using available sku_ids
    sku_items = []
    for i in range(random.randint(1, average_skus_per_order)):  # Random number of SKU items per order
        sku_id = random.choice(sku_ids)  # Choose a random sku_id from available ones
        sku_items.append({
            "sku_code": f"sku{str(uuid.uuid4().hex[:6]).upper()}",
            "sku_id": str(sku_id),
            "in_batch_code": f"batch{random.randint(1, 100)}",
            "sku_level": random.randint(0, 2),
            "amount": random.randint(1, 10),
            "production_date": int(time.time() * 1000) if random.choice([True, False]) else None,
            "expiration_date": int((datetime.now() + timedelta(days=random.randint(30, 365))).timestamp() * 1000) if random.choice([True, False]) else None
        })
    
    order = {
        "order_details": {
            "putaway_order_code": ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8)),
            "order_type": random.choice([0, 1]),
            "inbound_wave_code": f"wave_in_{random.randint(2020001, 2029999)}",
            "owner_code": random.choice(["lidong", "owner2", "owner3"]),
            "map_id": currentMapId,
            "print": {
                "type": random.choice([1, 2]),
                "content": '[{"field1":"value1"}]'
            },
            "carrier": {
                "type": random.choice([1, 2]),
                "code": random.choice(["DHL", "UPS", "FedEx"]),
                "name": random.choice(["DHL Freight", "UPS Express", "FedEx Ground"]),
                "waybill_code": f"D{random.randint(2020001, 2029999)}"
            },
            "dates": {
                "creation_date": int(time.time() * 1000),
                "expected_finish_date": int((datetime.now() + timedelta(hours=working_hours)).timestamp() * 1000)
            },
            "priority": random.choice([0, 1])
        },
        "sku_items": sku_items
    }

    putaway_request = PutawayRequest(
        header=PutawayHeader(
            warehouse_code="agv-sim",
            user_id="testUser",
            user_key="111111"
        ),
        body=PutawayBody(
            orders=[order]
        )
    )

    return putaway_request


# Endpoints
@router.post("/orders/putaway")
async def create_putaway_order(request: PutawayOrderRequest):

    currentMapId = request.currentMapId  # Get currentMapId from the request

    # Generate the putaway order
    new_order = await generate_putaway_order(currentMapId)

    # Convert to dictionary and insert into MongoDB
    order_dict = new_order.dict()
    await putaway_orders.insert_one(order_dict)

    putaway_order_code = order_dict["body"]["orders"][0]["order_details"]["putaway_order_code"]
    
    return {
        "message": "Putaway order created",
        "putaway_order_code": putaway_order_code
    }

@router.get("/orders/putaway/latest")
async def get_latest_putaway_order():
    order = await putaway_orders.find_one(sort=[("_id", -1)])
    if not order:
        raise HTTPException(status_code=404, detail="No putaway orders found")
    order["_id"] = str(order["_id"])
    return order


@router.get("/orders/putaway/by-code/{putaway_order_code}")
async def get_putaway_order_by_code(putaway_order_code: str):
    order = await putaway_orders.find_one({
        "body.orders.order_details.putaway_order_code": putaway_order_code
    })

    if not order:
        raise HTTPException(status_code=404, detail="Putaway order not found")
    order["_id"] = str(order["_id"])
    return order


@router.post("/orders/pick")
async def create_pick_order(data: PickRequest):
    await customer_orders.insert_one(data.dict())
    return {"message": "Pick order received"}
