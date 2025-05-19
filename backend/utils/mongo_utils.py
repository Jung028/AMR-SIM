# utils/mongo_utils.py

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)

# Database references
db_station = client["station_db"]
shelf_status = db_station["shelf_status"]
putaway_station = db_station["putaway_station"]

# putaway_tasks collection
db_task = client["task_db"]
putaway_tasks = db_task["putaway_tasks"]

# robot_status collection
db_robot = client["robot_db"]
robot_status = db_robot["robot_status"]
robot_metrics = db_robot["robot_metrics"] # Collection for robot metrics

# Create indexes for analytics
robot_metrics.create_index([("robot_id", 1)])
robot_metrics.create_index([("task_id", 1)])
robot_metrics.create_index([("task_start_time", -1)])
robot_metrics.create_index([("map_id", 1)])


# putaway_orders collection
db_orders = client["order_db"]
putaway_orders = db_orders["putaway_order_tracking"]
customer_orders = db_orders["customer_orders"]

# sku collection references
db_inventory = client["inventory_db"]
sku_collection = db_inventory["sku"]
storage_collection = db_inventory["storage"]
agv_goods_collection = db_inventory["agv_area_goods"]
shelf_status_collection = db_inventory["shelf_status"]

# simulation database, sku collection
db_sim = client["sim"]
sku_collection = db_sim["sku"]

# map collection
db_map = client["map"]  # Database name
maps_collection = db_map["map"]  # Collection name


# Utility function for ObjectId conversion
def mongo_to_dict(mongo_obj):
    if isinstance(mongo_obj, ObjectId):
        return str(mongo_obj)
    if isinstance(mongo_obj, dict):
        return {k: mongo_to_dict(v) for k, v in mongo_obj.items()}
    if isinstance(mongo_obj, list):
        return [mongo_to_dict(v) for v in mongo_obj]
    return mongo_obj

# Utility function to serialize MongoDB documents
def serialize_docs(docs):
    return [mongo_to_dict(doc) for doc in docs]

# Serialize any dictionary or list that contains ObjectIds
def serialize_dict(data):
    if isinstance(data, dict):
        return {k: serialize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_dict(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data
