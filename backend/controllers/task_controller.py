# controllers/task_controller.py
from fastapi import APIRouter, Query
from services.task_service import fetch_putaway_tasks, generate_putaway_tasks
from models.task_model import TaskGenerationRequest

router = APIRouter()

@router.get("/task/putaway-tasks")
async def get_putaway_tasks(map_id: str = Query(...)):
    return {"tasks": await fetch_putaway_tasks(map_id)}

@router.post("/task/generate-putaway")
async def generate_putaway(request: TaskGenerationRequest):
    print(f"Generating putaway tasks with mode: {request.mode}")
    if request.mode not in ["proximity", "energy", "load_balanced"]:
        return {"error": "Invalid mode. Choose from 'proximity', 'energy', or 'load_balanced'."}
    return await generate_putaway_tasks(mode=request.mode)
