from fastapi import APIRouter, HTTPException
from models.putaway_models import PickRequest, PutawayOrderRequest
from services.putaway_service import generate_putaway_order
from utils.mongo_utils import putaway_orders, customer_orders

router = APIRouter()

@router.post("/orders/putaway")
async def create_putaway_order(request: PutawayOrderRequest):
    new_order = await generate_putaway_order(request.currentMapId)
    order_dict = new_order.dict()
    await putaway_orders.insert_one(order_dict)
    return {
        "message": "Putaway order created",
        "putaway_order_code": order_dict["body"]["orders"][0]["order_details"]["putaway_order_code"]
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
