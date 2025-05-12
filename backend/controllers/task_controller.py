# controllers/task_controller.py
from fastapi import APIRouter, Query
from services.task_service import fetch_putaway_tasks, generate_putaway_tasks

router = APIRouter()

@router.get("/task/putaway-tasks")
async def get_putaway_tasks(map_id: str = Query(...)):
    return {"tasks": await fetch_putaway_tasks(map_id)}

@router.post("/task/generate-putaway")
async def generate_putaway():
    return await generate_putaway_tasks()
