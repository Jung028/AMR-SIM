from fastapi import APIRouter, HTTPException
from models.station_model import StationLoadUpdate
from services.station_service import update_station, add_station, get_stations

router = APIRouter()

@router.post("/station/load/update")
async def update_station_load(data: StationLoadUpdate):
    """Update putaway station load in the database."""
    try:
        await update_station(data)
        return {"message": "Putaway station load updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating station load: {str(e)}")

@router.post("/station/add-putaway-station")
async def add_putaway_station(data: StationLoadUpdate):
    """Add a new putaway station to the database."""
    try:
        success = await add_station(data)
        if not success:
            raise HTTPException(status_code=400, detail="Putaway station already exists for this map")
        return {"message": "Putaway station added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding putaway station: {str(e)}")

@router.get("/station/putaway-stations")
async def get_putaway_stations():
    """Retrieve all putaway stations from the database."""
    try:
        stations = await get_stations()
        if not stations:
            raise HTTPException(status_code=404, detail="No putaway stations available")
        return stations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching putaway stations: {str(e)}")
