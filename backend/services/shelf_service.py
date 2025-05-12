# services/shelf_service.py

from utils.mongo_utils import serialize_dict, shelf_status  # Import utility functions and collections
from models.shelf_model import ShelfStatusUpdate

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
    return serialize_dict(await shelves_cursor.to_list(length=None))
