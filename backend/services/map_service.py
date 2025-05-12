import json
import os
from bson import ObjectId
from fastapi import HTTPException, UploadFile
from models.map_model import MapRequest, UpdateMapRequest
from utils.mongo_utils import maps_collection


# Fetch available maps
async def get_maps_service():
    maps_cursor = maps_collection.find({}, {"name": 1})
    maps_list = await maps_cursor.to_list(length=100)
    return [{"_id": str(m["_id"]), "name": m["name"]} for m in maps_list]


# Fetch map by its ID
async def get_map_by_id_service(map_id: str):
    try:
        if not ObjectId.is_valid(map_id):
            raise HTTPException(status_code=400, detail="Invalid map ID format")

        map_data = await maps_collection.find_one({"_id": ObjectId(map_id)})
        if not map_data:
            raise HTTPException(status_code=404, detail="Map not found")

        map_data["_id"] = str(map_data["_id"])  # Convert ObjectId to str
        return map_data
    except Exception as e:
        print(f"Error loading map: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Save new map data
async def save_map_service(map_data: MapRequest):
    try:
        result = await maps_collection.insert_one(map_data.dict())
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error saving map: {e}")
        raise HTTPException(status_code=500, detail="Error saving map data")


# Update an existing map
async def update_map_service(id: str, update_data: UpdateMapRequest):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")

        map_to_update = await maps_collection.find_one({"_id": ObjectId(id)})
        if not map_to_update:
            raise HTTPException(status_code=404, detail="Map not found")

        result = await maps_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data.dict(exclude_unset=True)}
        )
        if result.modified_count:
            return {"message": "Map updated successfully"}
        raise HTTPException(status_code=404, detail="Map not found")
    except Exception as e:
        print(f"Error updating map: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Upload map data from file
async def upload_map_service(file: UploadFile):
    try:
        contents = await file.read()
        data = json.loads(contents)

        if "components" not in data or not isinstance(data["components"], list):
            raise HTTPException(status_code=400, detail="Invalid file format")

        map_data = MapRequest(
            name=data.get("name", "Unnamed Map"),
            rows=data.get("rows", 0),
            cols=data.get("cols", 0),
            components=data["components"]
        )

        result = await maps_collection.insert_one(map_data.dict())
        inserted_map_id = result.inserted_id

        inserted_map = await maps_collection.find_one({"_id": inserted_map_id})
        if not inserted_map:
            raise HTTPException(status_code=500, detail="Failed to retrieve inserted map")

        inserted_map["_id"] = str(inserted_map["_id"])

        updated_map_file_path = f"./updated_maps/{map_data.name}.json"
        os.makedirs(os.path.dirname(updated_map_file_path), exist_ok=True)
        with open(updated_map_file_path, 'w') as file:
            json.dump(map_data.dict(), file, indent=4)

        print(f"Map uploaded and loaded with ID: {inserted_map['_id']}")
        return inserted_map

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error decoding the JSON file")
    except Exception as e:
        print(f"Error uploading/loading map: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
