from pydantic import BaseModel
from typing import List, Optional


# SKU Bar Code Model
class SKUBarCode(BaseModel):
    sku_bar_code: str
    input_date: int


# SKU Packing Spec Model
class SKUPackingSpec(BaseModel):
    sku_packing_code: str
    sku_packing_length: float
    sku_packing_width: float
    sku_packing_height: float
    sku_packing_volume: float
    sku_packing_weight: float
    sku_packing_amount: int


# SKU Packing Model (Primary, Secondary, Tertiary)
class SKUPacking(BaseModel):
    sku_packing_spec: str
    primary: SKUPackingSpec
    secondary: SKUPackingSpec
    tertiary: SKUPackingSpec


# SKU Weight Model
class SKUWeight(BaseModel):
    sku_net_weight: float
    sku_gross_weight: float


# SKU Dimensions Model
class SKUDimensions(BaseModel):
    sku_length: float
    sku_width: float
    sku_height: float
    sku_volume: float


# SKU Attributes Model
class SKUAttributes(BaseModel):
    sku_size: str
    sku_color: str
    sku_style: str


# SKU Model (Main SKU Info)
class SKU(BaseModel):
    owner_code: str
    sku_id: str
    sku_code: str
    sku_name: str
    sku_price: float
    unit: str
    remark: Optional[str]
    dimensions: SKUDimensions
    weight: SKUWeight
    stock_limits: dict  # This can be a dictionary with `sku_min_count` and `sku_max_count`
    sku_shelf_life: int
    sku_specification: str
    sku_status: int
    sku_abc: str
    is_sequence_sku: int
    sku_production_location: str
    sku_brand: str
    sku_attributes: SKUAttributes
    sku_pic_url: str
    is_bar_code_full_update: int
    sku_bar_code_list: List[SKUBarCode]
    sku_packing: List[SKUPacking]


# Body Model (SKU Sync Request Body)
class SKUSyncRequestBody(BaseModel):
    sku_amount: int
    sku_list: List[SKU]


# Header Model (Request Header)
class SKUSyncRequestHeader(BaseModel):
    warehouse_code: str
    user_id: str
    user_key: str


# Full SKU Sync Request Model (combining header and body)
class SKUSyncRequest(BaseModel):
    header: SKUSyncRequestHeader
    body: SKUSyncRequestBody
