# app/controllers/google_sheets_controller.py

from fastapi import APIRouter, HTTPException
from services.google_sheets_service import get_google_sheets_data

router = APIRouter()

@router.get("/google-sheets-data")
async def get_google_sheets_data_endpoint():
    try:
        data = await get_google_sheets_data()
        return {"rows": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
