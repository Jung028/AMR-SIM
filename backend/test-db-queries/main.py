from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

app = FastAPI()

# Allow origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection URI
MONGO_URI = "mongodb+srv://admin:1234@cluster0.nby5v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client using Atlas URI
client = AsyncIOMotorClient(MONGO_URI)
db = client["map"]  # Database name
maps_collection = db["map"]  # Collection name

# Pydantic models
class Component(BaseModel):
    id: str
    type: str
    row: int
    col: int

class MapRequest(BaseModel):
    name: str
    rows: int
    cols: int
    components: List[Component]

class UpdateMapRequest(BaseModel):
    name: Optional[str]
    rows: Optional[int]
    cols: Optional[int]
    components: Optional[List[Component]]

@app.get("/")
async def root():
    return {"message": "API is working!"}

@app.get("/api/maps")
async def get_maps():
    # Fetch available maps from MongoDB Atlas
    maps_cursor = maps_collection.find({}, {"name": 1})
    maps_list = await maps_cursor.to_list(length=100)
    return [{"_id": str(m["_id"]), "name": m["name"]} for m in maps_list]

@app.get("/api/maps/id/{map_id}")
async def get_map_by_id(map_id: str):
    try:
        if not ObjectId.is_valid(map_id):
            raise HTTPException(status_code=400, detail="Invalid map ID format")

        map_data = await maps_collection.find_one({"_id": ObjectId(map_id)})
        if not map_data:
            raise HTTPException(status_code=404, detail="Map not found")
        
        map_data["_id"] = str(map_data["_id"])  # Convert ObjectId to str
        return map_data
    except Exception as e:
        print(f"Error loading map: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/maps")
async def save_map(map_data: MapRequest):
    try:
        # Save the map data into MongoDB
        result = await maps_collection.insert_one(map_data.dict())
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error saving map: {e}")  # Log the error
        raise HTTPException(status_code=500, detail="Error saving map data")

@app.put("/api/maps/{id}")
async def update_map(id: str, update_data: UpdateMapRequest):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")

        # Ensure the map exists before updating
        map_to_update = await maps_collection.find_one({"_id": ObjectId(id)})
        if not map_to_update:
            raise HTTPException(status_code=404, detail="Map not found")

        # Update the map data in MongoDB
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


@app.post("/api/maps/upload")
async def upload_map(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        contents = await file.read()
        data = json.loads(contents)

        # Ensure the data has the required format
        if "components" not in data or not isinstance(data["components"], list):
            raise HTTPException(status_code=400, detail="Invalid file format")

        # Assuming the file includes 'name', 'rows', and 'cols' fields
        map_data = MapRequest(
            name=data.get("name", "Unnamed Map"),
            rows=data.get("rows", 0),
            cols=data.get("cols", 0),
            components=data["components"]
        )

        # Save to MongoDB
        result = await maps_collection.insert_one(map_data.dict())

        # Save the updated file back to the local system (optional)
        updated_map_file_path = f"./updated_maps/{map_data.name}.json"
        os.makedirs(os.path.dirname(updated_map_file_path), exist_ok=True)
        with open(updated_map_file_path, 'w') as file:
            json.dump(map_data.dict(), file, indent=4)

        print(f"Map uploaded with ID: {result.inserted_id}")
        return {
            "inserted_id": str(result.inserted_id),
            "message": "Map uploaded and saved to MongoDB and file"
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error decoding the JSON file")
    except Exception as e:
        print(f"Error uploading map: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
