from pydantic import BaseModel
from typing import List, Optional

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

class SKUAttributes(BaseModel):
    sku_size: str
    sku_color: str
    sku_style: str

class SKUBarCode(BaseModel):
    sku_bar_code: str
    input_date: int

class SKUPackingSpec(BaseModel):
    sku_packing_spec: str
    primary: dict
    secondary: dict
    tertiary: dict

class SKUInfo(BaseModel):
    owner_code: str
    sku_id: str
    sku_code: str
    sku_name: str
    sku_price: float
    unit: str
    remark: str
    dimensions: Dimensions
    weight: Weight
    stock_limits: StockLimits
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
    sku_packing: List[SKUPackingSpec]

class SKUBody(BaseModel):
    sku_amount: int
    sku_list: List[SKUInfo]

class Header(BaseModel):
    warehouse_code: str
    user_id: str
    user_key: str

class SKUSyncRequest(BaseModel):
    header: Header
    body: SKUBody
