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



from controllers.task_controller import router as task_router
from controllers.station_controller import router as station_router
from controllers.shelf_controller import router as shelf_router
from controllers.robot_controller import router as robot_router
from controllers.putaway_controller import router as putaway_router
from controllers.inventory_controller import router as inventory_router
from controllers.google_sheets_controller import router as google_sheets_router
from controllers.sku_controller import router as sku_router
from controllers.map_controller import router as map_router


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




# ~~~~ Routers ~~~~


# Include the routers
app.include_router(inventory_router)
app.include_router(putaway_router)
app.include_router(task_router)
app.include_router(robot_router)
app.include_router(shelf_router)
app.include_router(station_router)
app.include_router(google_sheets_router)
app.include_router(sku_router)
app.include_router(map_router)

# ~~~~ END ~~~~


