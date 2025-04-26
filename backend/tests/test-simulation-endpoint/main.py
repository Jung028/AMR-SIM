from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.inventory_service import router as inventory_router
from services.order_service import router as order_router
from services.task_service import router as task_router
from services.robot_service import router as robot_router
from services.station_service import router as station_router

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the routers
app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(task_router)
app.include_router(robot_router)
app.include_router(station_router)
