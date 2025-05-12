from fastapi import APIRouter, HTTPException
from models.shelf_model import ShelfStatusUpdate
from services.shelf_service import update_shelf, add_shelf, get_shelves

router = APIRouter()

@router.post("/station/shelf/update")
async def update_shelf_status(data: ShelfStatusUpdate):
    """Update shelf status in the database."""
    try:
        result = await update_shelf(data)
        if result.modified_count > 0:
            return {"message": "Shelf status updated successfully"}
        elif result.upserted_id:
            return {"message": "Shelf created successfully"}
        else:
            raise HTTPException(status_code=400, detail="No changes made to shelf status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating shelf status: {str(e)}")

@router.post("/station/add-shelf")
async def add_shelf_route(data: ShelfStatusUpdate):
    """Add a new shelf to the database."""
    try:
        success = await add_shelf(data)
        if not success:
            raise HTTPException(status_code=400, detail="Shelf already exists for this map")
        return {"message": "Shelf added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding shelf: {str(e)}")

@router.get("/station/shelves")
async def get_shelves_route():
    """Retrieve all shelves from the database."""
    try:
        shelves = await get_shelves()
        if not shelves:
            raise HTTPException(status_code=404, detail="No shelves available")
        return shelves
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shelves: {str(e)}")
