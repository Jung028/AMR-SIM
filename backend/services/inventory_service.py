import os
from fastapi import APIRouter, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from math import floor

load_dotenv()

# MongoDB Connection Setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db_inv: AsyncIOMotorDatabase = client["inventory_db"]

# Collections
sku_collection = db_inv["sku"]
storage_collection = db_inv["storage"]
agv_goods_collection = db_inv["agv_area_goods"]
shelf_status_collection = db_inv["shelf_status"]  # Shelf status collection

router = APIRouter()

# ----------------------------- #
# Models
# ----------------------------- #

class Dimensions(BaseModel):
    sku_length: float  # meters
    sku_width: float   # meters
    sku_height: float  # meters
    sku_volume: float  # m³ (Calculated)

class Weight(BaseModel):
    sku_net_weight: float
    sku_gross_weight: float

class StockLimits(BaseModel):
    sku_min_count: int
    sku_max_count: int

class SkuAttributes(BaseModel):
    sku_size: Optional[str]
    sku_color: Optional[str]
    sku_style: Optional[str]

class Barcode(BaseModel):
    sku_bar_code: str
    input_date: int

class PackingLevel(BaseModel):
    sku_packing_code: str
    sku_packing_length: float
    sku_packing_width: float
    sku_packing_height: float
    sku_packing_volume: float
    sku_packing_weight: float
    sku_packing_amount: int

class SkuPacking(BaseModel):
    sku_packing_spec: str
    primary: PackingLevel
    secondary: Optional[PackingLevel]
    tertiary: Optional[PackingLevel]

class SKUItem(BaseModel):
    owner_code: str
    sku_id: str
    sku_code: str
    sku_name: str
    sku_price: float
    unit: str
    remark: Optional[str]
    dimensions: Dimensions
    weight: Weight
    stock_limits: StockLimits
    sku_shelf_life: int
    sku_specification: Optional[str]
    sku_status: int
    sku_abc: Optional[str]
    is_sequence_sku: int
    sku_production_location: Optional[str]
    sku_brand: Optional[str]
    sku_attributes: Optional[SkuAttributes]
    sku_pic_url: Optional[str]
    is_bar_code_full_update: int
    sku_bar_code_list: List[Barcode]
    sku_packing: List[SkuPacking]

class SKUSyncBody(BaseModel):
    sku_amount: int
    sku_list: List[SKUItem]

class SKUSyncRequest(BaseModel):
    header: Dict[str, Any]
    body: SKUSyncBody

class AGVUpdateRequest(BaseModel):
    sku_id: str
    qty: int

# ----------------------------- #
# Shelf Status Management
# ----------------------------- #

# Function to calculate how many items fit in available space (based on SKU volume and shelf space)
def calculate_max_capacity(shelf, sku):
    """Calculate how many SKUs can fit in the available space of a shelf level."""
    sku_volume = sku.dimensions.sku_volume  # Volume of one SKU in m³
    available_space = shelf['available_space']  # Available space in m³
    
    # Calculate how many SKUs fit in the available space
    max_capacity = floor(available_space / sku_volume)
    return max_capacity

# ----------------------------- #
# Endpoints
# ----------------------------- #

@router.post("/inventory/sku/create", status_code=status.HTTP_201_CREATED)
async def create_sku(data: SKUSyncRequest):
    inserted_ids = []
    for sku in data.body.sku_list:
        # Check if SKU already exists
        existing = await sku_collection.find_one({"sku_id": sku.sku_id})
        if existing:
            raise HTTPException(status_code=400, detail=f"SKU {sku.sku_id} already exists")
        
        # Insert the new SKU into the database
        result = await sku_collection.insert_one(sku.dict())
        inserted_ids.append(str(result.inserted_id))
        
        # Check if there is available space for this SKU in the shelf
        shelf_cursor = shelf_status_collection.find({"sku_id": sku.sku_id})
        shelves = await shelf_cursor.to_list(length=None)
        
        for shelf in shelves:
            max_capacity = calculate_max_capacity(shelf, sku)
            
            if max_capacity > 0:
                # Update the shelf status with new quantity and space left
                shelf['sku_quantity'] += max_capacity
                shelf['available_space'] -= max_capacity * sku.dimensions.sku_volume  # Reduce space
                
                # Update the shelf in the database
                await shelf_status_collection.update_one(
                    {"_id": shelf["_id"]},
                    {"$set": {"sku_quantity": shelf['sku_quantity'], "available_space": shelf['available_space']}}
                )

    return {"message": "SKU(s) created", "inserted_ids": inserted_ids}


@router.get("/inventory/sku/{sku_id}")
async def get_sku_details(sku_id: str):
    item = await sku_collection.find_one({"sku_id": sku_id})
    if not item:
        raise HTTPException(status_code=404, detail="SKU not found")
    item["_id"] = str(item["_id"])
    return item


@router.get("/inventory/stock/{sku_id}")
async def get_stock(sku_id: str):
    warehouse_stock = await storage_collection.find_one({"sku_id": sku_id}) or {"qty": 0}
    agv_stock = await agv_goods_collection.find_one({"sku_id": sku_id}) or {"qty": 0}
    return {
        "warehouse_qty": warehouse_stock.get("qty", 0),
        "agv_area_qty": agv_stock.get("qty", 0)
    }


@router.post("/inventory/agv/update", status_code=status.HTTP_200_OK)
async def update_agv_area_goods(data: AGVUpdateRequest):
    await agv_goods_collection.update_one(
        {"sku_id": data.sku_id},
        {"$inc": {"qty": data.qty}},
        upsert=True
    )
    return {"message": "AGV area stock updated"}
