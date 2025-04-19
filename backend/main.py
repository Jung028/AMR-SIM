# backend/main.py

from fastapi import FastAPI
from services.inventory_service import router as inventory_router
from services.order_service import router as order_router
from services.task_service import router as task_router
from services.robot_service import router as robot_router
from services.station_service import router as station_router

app = FastAPI()

app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(task_router)
app.include_router(robot_router)
app.include_router(station_router)
