
# services/inventory_service.py
from fastapi import HTTPException
from math import floor
from utils.mongo_utils import sku_collection, storage_collection, agv_goods_collection, shelf_status_collection
from models.inventory_models import SKUSyncRequest, AGVUpdateRequest

async def handle_sku_creation(data: SKUSyncRequest):
    inserted_ids = []
    for sku in data.body.sku_list:
        existing = await sku_collection.find_one({"sku_id": sku.sku_id})
        if existing:
            raise HTTPException(status_code=400, detail=f"SKU {sku.sku_id} already exists")

        result = await sku_collection.insert_one(sku.dict())
        inserted_ids.append(str(result.inserted_id))

        shelf_cursor = shelf_status_collection.find({"sku_id": sku.sku_id})
        shelves = await shelf_cursor.to_list(length=None)

        for shelf in shelves:
            max_capacity = calculate_max_capacity(shelf, sku)
            if max_capacity > 0:
                shelf['sku_quantity'] += max_capacity
                shelf['available_space'] -= max_capacity * sku.dimensions.sku_volume
                await shelf_status_collection.update_one(
                    {"_id": shelf["_id"]},
                    {"$set": {"sku_quantity": shelf['sku_quantity'], "available_space": shelf['available_space']}}
                )

    return {"message": "SKU(s) created", "inserted_ids": inserted_ids}

async def get_sku_by_id(sku_id: str):
    item = await sku_collection.find_one({"sku_id": sku_id})
    if not item:
        raise HTTPException(status_code=404, detail="SKU not found")
    item["_id"] = str(item["_id"])
    return item

async def get_stock_by_sku_id(sku_id: str):
    warehouse_stock = await storage_collection.find_one({"sku_id": sku_id}) or {"qty": 0}
    agv_stock = await agv_goods_collection.find_one({"sku_id": sku_id}) or {"qty": 0}
    return {
        "warehouse_qty": warehouse_stock.get("qty", 0),
        "agv_area_qty": agv_stock.get("qty", 0)
    }

async def update_agv_stock(data: AGVUpdateRequest):
    await agv_goods_collection.update_one(
        {"sku_id": data.sku_id},
        {"$inc": {"qty": data.qty}},
        upsert=True
    )
    return {"message": "AGV area stock updated"}

def calculate_max_capacity(shelf, sku):
    sku_volume = sku.dimensions.sku_volume
    available_space = shelf['available_space']
    return floor(available_space / sku_volume)
