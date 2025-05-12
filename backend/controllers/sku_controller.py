from fastapi import APIRouter, HTTPException
from models.sku_model import SKURequest
from services.sku_service import save_sku_service, get_sku_service, get_all_skus_service

router = APIRouter()

@router.post("/save-sku/")
async def save_sku(data: SKURequest):
    try:
        return await save_sku_service(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error saving SKU data: " + str(e))


@router.get("/get-sku/{sku_id}")
async def get_sku(sku_id: str):
    try:
        return await get_sku_service(sku_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching SKU data: " + str(e))


@router.get("/get-all-skus")
async def get_all_skus(skip: int = 0, limit: int = 10):
    try:
        return await get_all_skus_service(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching SKUs: " + str(e))
