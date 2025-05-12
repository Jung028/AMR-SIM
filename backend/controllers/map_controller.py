from fastapi import APIRouter, HTTPException, UploadFile, File
from models.map_model import MapRequest, UpdateMapRequest
from services.map_service import (
    get_maps_service, 
    get_map_by_id_service, 
    save_map_service, 
    update_map_service, 
    upload_map_service
)

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "API is working!"}

@router.get("/api/maps")
async def get_maps():
    return await get_maps_service()

@router.get("/api/maps/id/{map_id}")
async def get_map_by_id(map_id: str):
    return await get_map_by_id_service(map_id)

@router.post("/api/maps")
async def save_map(map_data: MapRequest):
    return await save_map_service(map_data)

@router.put("/api/maps/{id}")
async def update_map(id: str, update_data: UpdateMapRequest):
    return await update_map_service(id, update_data)

@router.post("/api/maps/upload")
async def upload_map(file: UploadFile = File(...)):
    return await upload_map_service(file)
