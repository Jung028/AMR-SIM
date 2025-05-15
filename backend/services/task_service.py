# services/task_service.py
from fastapi import HTTPException
import httpx
import random
from utils.mongo_utils import serialize_dict, putaway_tasks  # Import utility functions and MongoDB collections

async def fetch_putaway_tasks(map_id: str):
    try:
        tasks = await putaway_tasks.find({"map_id": map_id}).to_list(length=100)
        return [serialize_dict(task) for task in tasks]
    except Exception:
        raise HTTPException(status_code=500, detail="Error fetching putaway tasks")

async def generate_putaway_tasks(mode: str = "proximity"):
    MAX_TASKS_PER_ROBOT = 3
    BATTERY_THRESHOLD = 60.0
    
    try:
        async with httpx.AsyncClient() as client:
            order_response = await client.get("http://localhost:8000/orders/putaway/latest")
            order_response.raise_for_status()
            order = order_response.json().get("body", {}).get("orders", [{}])[0]

            putaway_order_code = order.get("order_details", {}).get("putaway_order_code")
            map_id = order.get("order_details", {}).get("map_id")
            sku_items = order.get("sku_items", [])

            if not putaway_order_code or not map_id or not sku_items:
                raise HTTPException(status_code=400, detail="Incomplete order data")

            robots = (await client.get(f"http://localhost:8000/robots/idle?map_id={map_id}")).json().get("robots", [])
            if not robots:
                raise HTTPException(status_code=404, detail="No available robots")

            # Filter out robots with low battery
            robots = [r for r in robots if r.get("battery_level", 0) >= BATTERY_THRESHOLD]
            if not robots:
                raise HTTPException(status_code=404, detail="No robots with sufficient battery available")

            # Sort robots based on selected mode
            if mode == "proximity":
                sorted_robots = sorted(robots, key=lambda r: r["location"]["x"])
            elif mode == "energy":
                sorted_robots = sorted(robots, key=lambda r: r["battery_level"], reverse=True)
            elif mode == "load_balanced":
                sorted_robots = sorted(robots, key=lambda r: r.get("filled_space", 0))
            else:
                raise HTTPException(status_code=400, detail=f"Unknown AGV mode: {mode}")

            robot_task_counts = {r["robot_id"]: 0 for r in sorted_robots}
            robot_index = 0

            shelves = (await client.get(f"http://localhost:8000/station/shelves?map_id={map_id}")).json()
            if not shelves:
                raise HTTPException(status_code=404, detail="No shelves found")

            sku_dimensions = {}
            for sku in sku_items:
                sku_info = (await client.get(f"http://localhost:8000/get-sku/{sku['sku_id']}")).json()
                primary = sku_info["sku_data"]["sku_packing"][0].get("primary")
                if not primary:
                    raise HTTPException(status_code=400, detail=f"Missing packing data for {sku['sku_id']}")
                sku_dimensions[sku["sku_id"]] = {
                    "volume": primary.get("sku_packing_volume", 0.0),
                    "height": primary.get("sku_packing_height", 0.0)
                }

            putaway_tasks_created = []

            for sku in sku_items:
                sku_id = sku["sku_id"]
                amount_remaining = sku["amount"]
                volume = sku_dimensions[sku_id]["volume"]
                height = sku_dimensions[sku_id]["height"]

                for shelf in sorted(shelves, key=lambda s: s["available_space"], reverse=True):
                    if amount_remaining <= 0:
                        break
                    for level_name in ["third", "second", "ground"]:
                        level = shelf["shelf_levels"].get(level_name)
                        if not level or height > level.get("max_height", float('inf')):
                            continue

                        units_fit = int(level["available_space"] // volume)
                        units_to_place = min(units_fit, amount_remaining)

                        if units_to_place > 0:
                            level["available_space"] -= units_to_place * volume
                            shelf["available_space"] -= units_to_place * volume
                            level.setdefault("sku_details", []).append({"sku_id": sku_id, "amount": units_to_place})

                            stations = (await client.get(f"http://localhost:8000/station/putaway-stations?map_id={map_id}")).json()
                            if not stations:
                                raise HTTPException(status_code=404, detail="No stations found")

                            station = sorted(stations, key=lambda s: s["queue_length"])[0]

                            for _ in range(len(sorted_robots)):
                                current_robot = sorted_robots[robot_index]
                                if robot_task_counts[current_robot["robot_id"]] < MAX_TASKS_PER_ROBOT:
                                    assigned_robot = current_robot
                                    robot_task_counts[current_robot["robot_id"]] += 1
                                    break
                                robot_index = (robot_index + 1) % len(sorted_robots)
                            else:
                                raise HTTPException(status_code=500, detail="Not enough robot capacity")

                            task = {
                                "task_id": f"TASK_{random.randint(1000, 9999)}",
                                "putaway_order_code": putaway_order_code,
                                "robot_id": assigned_robot["robot_id"],
                                "station_id": station["station_id"],
                                "map_id": map_id,
                                "shelf_id": shelf["shelf_id"],
                                "level": level_name,
                                "sku_id": sku_id,
                                "amount": units_to_place,
                                "status": "pending"
                            }
                            putaway_tasks_created.append(task)
                            amount_remaining -= units_to_place
                            break
                if amount_remaining > 0:
                    raise HTTPException(status_code=400, detail=f"Insufficient space for SKU {sku_id}")

        response_tasks = []
        for task in putaway_tasks_created:
            result = await putaway_tasks.insert_one(task)
            task["_id"] = str(result.inserted_id)
            response_tasks.append(task)

        return {"message": "Putaway tasks created", "tasks": response_tasks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate task: {str(e)}")
