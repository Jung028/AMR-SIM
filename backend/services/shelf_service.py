from utils.mongo_utils import shelf_status
from bson import ObjectId
from models.shelf_model import ShelfStatusUpdate

def mongo_to_dict(mongo_obj):
    if isinstance(mongo_obj, ObjectId):
        return str(mongo_obj)
    if isinstance(mongo_obj, dict):
        return {k: mongo_to_dict(v) for k, v in mongo_obj.items()}
    if isinstance(mongo_obj, list):
        return [mongo_to_dict(v) for v in mongo_obj]
    return mongo_obj

def serialize_docs(docs):
    return [mongo_to_dict(doc) for doc in docs]

async def update_shelf(data: ShelfStatusUpdate):
    update_data = {
        "shelf_capacity": data.shelf_capacity,
        "available_space": data.available_space,
        "shelf_levels": data.shelf_levels,
        "map_id": data.map_id
    }
    return await shelf_status.update_one(
        {"shelf_id": data.shelf_id, "map_id": data.map_id},
        {"$set": update_data},
        upsert=True
    )

async def add_shelf(data: ShelfStatusUpdate):
    existing = await shelf_status.find_one({"shelf_id": data.shelf_id, "map_id": data.map_id})
    if existing:
        return False
    await shelf_status.insert_one(data.dict())
    return True

async def get_shelves():
    shelves_cursor = shelf_status.find()
    return serialize_docs(await shelves_cursor.to_list(length=None))
