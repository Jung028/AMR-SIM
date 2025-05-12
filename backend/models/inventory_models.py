
# models/inventory_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Dimensions(BaseModel):
    sku_length: float
    sku_width: float
    sku_height: float
    sku_volume: float

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

