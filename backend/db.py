# db.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import AsyncGenerator
import os

# MongoDB URI from Atlas
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:1234@cluster0.nby5v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "map"  # You can change this to your actual DB name

# Dependency to get the DB connection
async def get_db() -> AsyncGenerator:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()
