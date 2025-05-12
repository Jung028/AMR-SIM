# controllers/inventory_controller.py
from fastapi import APIRouter, HTTPException, status
from models.inventory_models import SKUSyncRequest, AGVUpdateRequest
from services.inventory_service import handle_sku_creation, get_sku_by_id, get_stock_by_sku_id, update_agv_stock

router = APIRouter()

@router.post("/inventory/sku/create", status_code=status.HTTP_201_CREATED)
async def create_sku(data: SKUSyncRequest):
    return await handle_sku_creation(data)

@router.get("/inventory/sku/{sku_id}")
async def get_sku_details(sku_id: str):
    return await get_sku_by_id(sku_id)

@router.get("/inventory/stock/{sku_id}")
async def get_stock(sku_id: str):
    return await get_stock_by_sku_id(sku_id)

@router.post("/inventory/agv/update", status_code=status.HTTP_200_OK)
async def update_agv_area_goods(data: AGVUpdateRequest):
    return await update_agv_stock(data)

