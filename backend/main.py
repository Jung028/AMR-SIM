from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv  # Import the dotenv module
from pymongo import MongoClient

from services.inventory_service import router as inventory_router
from services.order_service import router as order_router
from services.robot_service import router as robot_router


from controllers.task_controller import router as task_controller
from controllers.station_controller import router as station_router
from controllers.shelf_controller import router as shelf_router



# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Allow origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],  # or ["*"] for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ~~~~ GOOGLE SHEETS CONNECTION AND RETRIEVAL ~~~~

# Google Sheets API authentication
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1ylZxBM7yyCzBeP7Hu-MfD88tE0QSKlkYibf58PQLWbc'  # Your Google Sheet ID
RANGE_NAME = 'Sheet2!B87:E92'  # The range you want to fetch

# Authenticate and build the service
def get_sheets_service():
    creds, _ = google.auth.load_credentials_from_file('credentials.json', SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

@app.get("/google-sheets-data")
async def get_google_sheets_data():
    service = get_sheets_service()

    try:
        # Fetch data from Google Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        # Format the data into rows
        rows = []
        for row in values:
            rows.append({"data": row})  # Adjust the structure as needed

        return {"rows": rows}
    except HttpError as err:
        return {"error": f"An error occurred: {err}"}

# ~~~~ END ~~~~


# ~~~~ MONGODB CONNECTION AND RETRIEVAL ~~~~

# Load MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")  # Fetch the MongoDB URI from the environment variable

# Initialize MongoDB client using Atlas URI
client = AsyncIOMotorClient(MONGO_URI)
db_map = client["map"]  # Database name
maps_collection = db_map["map"]  # Collection name

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

        # Create map data object
        map_data = MapRequest(
            name=data.get("name", "Unnamed Map"),
            rows=data.get("rows", 0),
            cols=data.get("cols", 0),
            components=data["components"]
        )

        # Insert into MongoDB
        result = await maps_collection.insert_one(map_data.dict())
        inserted_map_id = result.inserted_id

        # Load the full inserted map
        inserted_map = await maps_collection.find_one({"_id": inserted_map_id})
        if not inserted_map:
            raise HTTPException(status_code=500, detail="Failed to retrieve inserted map")

        # Convert ObjectId to string for JSON response
        inserted_map["_id"] = str(inserted_map["_id"])

        # (Optional) Save JSON locally
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



# ~~~~ END ~~~~
from bson import ObjectId

# Helper function to convert ObjectId to string
def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

# ~~~~ SIMULATION ENDPOINTS ~~~~

db_sim = client["sim"]  # Database name


sku_collection = db_sim['sku']
putaway_collection = db_sim['putaway']
picking_collection = db_sim['picking']


# Pydantic model
class SKURequest(BaseModel):
    header: dict
    body: dict

# For combined simulation request
class SimulationRequest(BaseModel):
    putaway: SKURequest
    picking: SKURequest

# Original SKU endpoint
@app.post("/save-sku/")
async def save_sku(data: SKURequest):
    try:
        sku_data = {"header": data.header, "body": data.body}
        result = await sku_collection.insert_one(sku_data)
        return {"message": "SKU data saved successfully", "sku_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error saving SKU data: " + str(e))
    

# GET method for SKU collection
@app.get("/get-sku/{sku_id}")
async def get_sku(sku_id: str):
    try:
        # Searching within the sku_list array where sku_id matches
        sku = await sku_collection.find_one({"body.sku_list.sku_id": sku_id})
        
        if sku is None:
            raise HTTPException(status_code=404, detail=f"SKU {sku_id} not found")
        
        # You might want to extract only the relevant data inside the body.sku_list
        sku_data = next((item for item in sku["body"]["sku_list"] if item["sku_id"] == sku_id), None)
        
        if sku_data is None:
            raise HTTPException(status_code=404, detail=f"SKU {sku_id} not found in sku_list")
        
        return {"sku_id": sku_id, "sku_data": sku_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching SKU data: " + str(e))


# GET method for Putaway collection
@app.get("/get-putaway/{putaway_id}")
async def get_putaway(putaway_id: str):
    try:
        putaway = await putaway_collection.find_one({"_id": putaway_id})
        if putaway is None:
            raise HTTPException(status_code=404, detail="Putaway data not found")
        return {"putaway_id": putaway_id, "putaway_data": putaway}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching Putaway data: " + str(e))

# GET method for Picking collection
@app.get("/get-picking/{picking_id}")
async def get_picking(picking_id: str):
    try:
        picking = await picking_collection.find_one({"_id": picking_id})
        if picking is None:
            raise HTTPException(status_code=404, detail="Picking data not found")
        return {"picking_id": picking_id, "picking_data": picking}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching Picking data: " + str(e))

# GET method for all SKUs (optional)
@app.get("/get-all-skus")
async def get_all_skus(skip: int = 0, limit: int = 10):
    try:
        # Fetching SKUs from the collection
        skus = await sku_collection.find().skip(skip).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string for each SKU
        skus = convert_objectid(skus)

        return {"skus": skus}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching SKUs: " + str(e))

# Save putaway
@app.post("/save-putaway/")
async def save_putaway(data: SKURequest):
    try:
        document = {"header": data.header, "body": data.body}
        result = putaway_collection.insert_one(document)
        return {"message": "Putaway data saved successfully", "sku_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving putaway data: {str(e)}")

# Save picking
@app.post("/save-picking/")
async def save_picking(data: SKURequest):
    try:
        document = {"header": data.header, "body": data.body}
        result = picking_collection.insert_one(document)
        return {"message": "Picking data saved successfully", "sku_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving picking data: {str(e)}")


# ~~~~ END ~~~~


# ~~~~ Routers ~~~~


# Include the routers
app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(task_controller)
app.include_router(robot_router)
app.include_router(shelf_router)
app.include_router(station_router)

# ~~~~ END ~~~~


