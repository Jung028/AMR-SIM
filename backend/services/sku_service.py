# services/sku_service.py

from utils.mongo_utils import sku_collection, mongo_to_dict

# Service to save SKU data
async def save_sku_service(data):
    sku_data = {"header": data.header, "body": data.body}
    result = await sku_collection.insert_one(sku_data)
    return {"message": "SKU data saved successfully", "sku_id": str(result.inserted_id)}

# Service to get SKU by sku_id
async def get_sku_service(sku_id: str):
    sku = await sku_collection.find_one({"body.sku_list.sku_id": sku_id})
    
    if sku is None:
        raise Exception(f"SKU {sku_id} not found")
    
    sku_data = next((item for item in sku["body"]["sku_list"] if item["sku_id"] == sku_id), None)
    
    if sku_data is None:
        raise Exception(f"SKU {sku_id} not found in sku_list")
    
    return {"sku_id": sku_id, "sku_data": sku_data}

# Service to get all SKUs with pagination
async def get_all_skus_service(skip: int, limit: int):
    skus = await sku_collection.find().skip(skip).limit(limit).to_list(length=limit)
    skus = mongo_to_dict(skus)
    return {"skus": skus}
