from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['map']
sku_collection = db['sku']
putaway_collection = db['putaway']
picking_collection = db['picking']

# FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        result = sku_collection.insert_one(sku_data)
        return {"message": "SKU data saved successfully", "sku_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error saving SKU data: " + str(e))

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

# New: Start simulation (saves both putaway & picking)
@app.post("/start-simulation/")
async def start_simulation(data: SimulationRequest):
    try:
        putaway_doc = {"header": data.putaway.header, "body": data.putaway.body}
        picking_doc = {"header": data.picking.header, "body": data.picking.body}

        putaway_result = putaway_collection.insert_one(putaway_doc)
        picking_result = picking_collection.insert_one(picking_doc)

        return {
            "message": "Simulation data saved successfully",
            "putaway_id": str(putaway_result.inserted_id),
            "picking_id": str(picking_result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error during simulation: {str(e)}")
