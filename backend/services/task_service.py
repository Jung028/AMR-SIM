# services/task_service.py
from fastapi import HTTPException
import httpx
import random
from utils.mongo_utils import serialize_dict, putaway_tasks # Import utility functions and MongoDB collections

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
            # 1. Fetch Order Details
            order_response = await client.get("http://localhost:8000/orders/putaway/latest")
            order_response.raise_for_status()
            order_body = order_response.json().get("body", {})
            orders_list = order_body.get("orders", [])
            if not orders_list:
                raise HTTPException(status_code=404, detail="No putaway orders found")
            order = orders_list[0]

            order_details = order.get("order_details", {})
            putaway_order_code = order_details.get("putaway_order_code")
            map_id = order_details.get("map_id")
            sku_items = order.get("sku_items", [])

            if not putaway_order_code or not map_id or not sku_items:
                raise HTTPException(status_code=400, detail="Incomplete order data: missing order code, map_id, or SKU items")

            # 2. Fetch and Prepare Robots
            robots_response = await client.get(f"http://localhost:8000/robots/idle?map_id={map_id}")
            robots_response.raise_for_status()
            robots_data = robots_response.json().get("robots", [])
            
            if not robots_data:
                raise HTTPException(status_code=404, detail=f"No idle robots found for map_id {map_id}")

            available_robots_list = [r for r in robots_data if r.get("battery_level", 0) >= BATTERY_THRESHOLD]
            if not available_robots_list:
                raise HTTPException(status_code=404, detail="No robots with sufficient battery available")

            if mode == "proximity":
                sorted_robots = sorted(available_robots_list, key=lambda r: r.get("location", {}).get("x", 0))
            elif mode == "energy":
                sorted_robots = sorted(available_robots_list, key=lambda r: r["battery_level"], reverse=True)
            elif mode == "load_balanced":
                sorted_robots = sorted(available_robots_list, key=lambda r: r.get("filled_space", 0))
            else:
                raise HTTPException(status_code=400, detail=f"Unknown AGV mode: {mode}")
            
            num_available_robots = len(sorted_robots)
            robot_task_counts = {r["robot_id"]: 0 for r in sorted_robots}
            robot_selection_index = 0 

            # 3. Fetch Shelves Data
            shelves_response = await client.get(f"http://localhost:8000/station/shelves?map_id={map_id}")
            shelves_response.raise_for_status()
            all_shelves_data = shelves_response.json() # This list will be modified in-place (available_space)
            if not all_shelves_data:
                raise HTTPException(status_code=404, detail=f"No shelves found for map_id {map_id}")

            # 4. Fetch SKU Dimensions
            sku_dimensions = {}
            for sku_item_for_dim_fetch in sku_items:
                sku_id_for_dim = sku_item_for_dim_fetch["sku_id"]
                if sku_id_for_dim in sku_dimensions: continue

                sku_info_response = await client.get(f"http://localhost:8000/get-sku/{sku_id_for_dim}")
                sku_info_response.raise_for_status()
                sku_info = sku_info_response.json()
                sku_data = sku_info.get("sku_data", {})
                sku_packing_list = sku_data.get("sku_packing", [])
                if not sku_packing_list:
                    raise HTTPException(status_code=400, detail=f"Missing packing data: sku_packing list empty for SKU {sku_id_for_dim}")
                
                first_packing_obj = sku_packing_list[0]
                if not isinstance(first_packing_obj, dict):
                    raise HTTPException(status_code=400, detail=f"First packing object for SKU {sku_id_for_dim} is not a dictionary.")
                
                actual_dimensions_dict = first_packing_obj.get("primary")
                if not actual_dimensions_dict or not isinstance(actual_dimensions_dict, dict):
                    raise HTTPException(status_code=400, detail=f"Primary packing data for SKU {sku_id_for_dim} missing or invalid.")

                volume = float(actual_dimensions_dict.get("sku_packing_volume", 0.0))
                height = float(actual_dimensions_dict.get("sku_packing_height", 0.0))

                if not (isinstance(volume, float) and isinstance(height, float)): # Already converted to float
                    raise HTTPException(status_code=400, detail=f"Volume or height for SKU {sku_id_for_dim} is not a valid number.")
                if volume <= 0 or height <= 0:
                    raise HTTPException(status_code=400, detail=f"SKU {sku_id_for_dim} has invalid volume or height (must be > 0).")
                
                sku_dimensions[sku_id_for_dim] = {"volume": volume, "height": height}

            # 5. Generate Putaway Tasks (New Logic)
            putaway_tasks_generated = []

            for sku_item_data in sku_items:
                sku_id = sku_item_data["sku_id"]
                total_amount_for_sku_item = sku_item_data["amount"]

                if not isinstance(total_amount_for_sku_item, int) or total_amount_for_sku_item <= 0:
                    continue # Skip SKUs with invalid or zero amount

                current_sku_props = sku_dimensions.get(sku_id)
                if not current_sku_props: # Should be caught by pre-fetching logic
                    raise HTTPException(status_code=500, detail=f"Internal error: Dimensions for SKU {sku_id} not pre-fetched.")
                
                sku_volume = current_sku_props["volume"]
                sku_height = current_sku_props["height"]
                amount_of_sku_item_placed_globally = 0

                while amount_of_sku_item_placed_globally < total_amount_for_sku_item:
                    # --- Robot Selection for this shelf-task ---
                    assigned_robot = None
                    for _ in range(num_available_robots):
                        candidate_robot = sorted_robots[robot_selection_index]
                        if robot_task_counts[candidate_robot["robot_id"]] < MAX_TASKS_PER_ROBOT:
                            assigned_robot = candidate_robot
                            break
                        robot_selection_index = (robot_selection_index + 1) % num_available_robots
                    
                    if not assigned_robot:
                        raise HTTPException(status_code=500, detail=f"Not enough robot capacity available for SKU {sku_id}. All robots at MAX_TASKS_PER_ROBOT.")

                    # --- Shelf Selection for this shelf-task ---
                    eligible_shelves_for_sku = []
                    for shelf_candidate in all_shelves_data:
                        if shelf_candidate.get("available_space", 0) > 0: # Basic check for overall space
                            can_fit_on_any_level = False
                            shelf_levels_data = shelf_candidate.get("shelf_levels", {})
                            if isinstance(shelf_levels_data, dict): # Ensure it's a dict
                                for level_details in shelf_levels_data.values():
                                    if (level_details.get("available_space", 0) > 0 and
                                        sku_height <= level_details.get("max_height", float('inf')) and
                                        int(level_details.get("available_space", 0) // sku_volume) >= 1): # Can fit at least one unit
                                        can_fit_on_any_level = True
                                        break
                            if can_fit_on_any_level:
                                eligible_shelves_for_sku.append(shelf_candidate)
                    
                    if not eligible_shelves_for_sku:
                        raise HTTPException(status_code=400, detail=f"Insufficient space or no suitable shelf found for SKU {sku_id} (height/volume constraints). Remaining: {total_amount_for_sku_item - amount_of_sku_item_placed_globally}")

                    # Sort eligible shelves (e.g., by most available space)
                    # The definition of "best" shelf can vary. Largest available_space is common.
                    # The in-memory `all_shelves_data` is updated, so this sort uses current states.
                    current_selected_shelf = sorted(eligible_shelves_for_sku, key=lambda s: s.get("available_space", 0), reverse=True)[0]

                    # --- Station Selection ---
                    stations_response = await client.get(f"http://localhost:8000/station/putaway-stations?map_id={map_id}")
                    stations_response.raise_for_status()
                    putaway_stations = stations_response.json()
                    if not putaway_stations:
                        raise HTTPException(status_code=404, detail="No putaway stations found.")
                    selected_station = sorted(putaway_stations, key=lambda s: s.get("queue_length", 0))[0]

                    # --- Process selected shelf for the current SKU ---
                    placements_on_this_shelf = []
                    total_units_placed_on_this_shelf = 0
                    
                    shelf_levels_to_process = current_selected_shelf.get("shelf_levels", {})
                    # Iterate through levels in a defined order (e.g., top-down)
                    for level_name in ["third", "second", "ground"]:
                        if amount_of_sku_item_placed_globally >= total_amount_for_sku_item:
                            break # SKU item fully placed globally

                        level_data = shelf_levels_to_process.get(level_name)
                        if not level_data or level_data.get("available_space", 0) <= 0 or sku_height > level_data.get("max_height", float('inf')):
                            continue # Skip level: no data, no space, or SKU too tall

                        units_fit_on_level = int(level_data["available_space"] // sku_volume)
                        amount_needed_globally_for_sku = total_amount_for_sku_item - amount_of_sku_item_placed_globally
                        units_to_place_on_level = min(units_fit_on_level, amount_needed_globally_for_sku)

                        if units_to_place_on_level > 0:
                            placements_on_this_shelf.append({
                                "level": level_name,
                                "sku_id": sku_id, # Included for clarity within placement details
                                "amount": units_to_place_on_level
                            })
                            
                            level_data["available_space"] -= units_to_place_on_level * sku_volume
                            current_selected_shelf["available_space"] -= units_to_place_on_level * sku_volume
                            level_data.setdefault("sku_details", []).append({"sku_id": sku_id, "amount": units_to_place_on_level})

                            total_units_placed_on_this_shelf += units_to_place_on_level
                            amount_of_sku_item_placed_globally += units_to_place_on_level
                    
                    # --- Create a task if items were placed on this shelf ---
                    if total_units_placed_on_this_shelf > 0:
                        task = {
                            "task_id": f"TASK_{random.randint(1000, 9999)}", # Original task_id format
                            "putaway_order_code": putaway_order_code,
                            "robot_id": assigned_robot["robot_id"],
                            "station_id": selected_station["station_id"],
                            "map_id": map_id,
                            "shelf_id": current_selected_shelf["shelf_id"],
                            "sku_id": sku_id, # The SKU this task is for
                            "total_amount_on_shelf": total_units_placed_on_this_shelf, # Total of this SKU placed on this shelf for this task
                            "placements": placements_on_this_shelf, # List of {level, sku_id, amount}
                            "status": "pending"
                        }
                        putaway_tasks_generated.append(task)

                        robot_task_counts[assigned_robot["robot_id"]] += 1
                        robot_selection_index = (robot_selection_index + 1) % num_available_robots
                    
                    # If no units were placed on this shelf, but SKU still needs placing, the outer `while` loop
                    # will re-evaluate. If eligible_shelves becomes empty, an error is raised above.
                    # This check helps prevent infinite loops if shelf selection logic has a flaw.
                    elif amount_of_sku_item_placed_globally < total_amount_for_sku_item and not eligible_shelves_for_sku:
                         raise HTTPException(status_code=400, detail=f"Logical error or no viable shelf: SKU {sku_id} has remaining units but no placeable shelf was found.")


                if amount_of_sku_item_placed_globally < total_amount_for_sku_item:
                    raise HTTPException(status_code=400, detail=f"Insufficient total capacity for SKU {sku_id}. Placed {amount_of_sku_item_placed_globally}/{total_amount_for_sku_item}.")

            # 6. Store and Respond with Tasks
            response_tasks = []
            if putaway_tasks_generated:
                results = await putaway_tasks.insert_many([task.copy() for task in putaway_tasks_generated]) # Use .copy() for safety
                for i, task_obj in enumerate(putaway_tasks_generated):
                    # Create a new dict for response to avoid modifying the list sent to insert_many if it was not copied
                    response_task_item = task_obj.copy() 
                    response_task_item["_id"] = str(results.inserted_ids[i])
                    response_tasks.append(response_task_item)

            return {"message": "Putaway tasks generated successfully based on shelf capacity.", "tasks": response_tasks}

    except httpx.HTTPStatusError as e:
        error_detail = f"HTTP error communicating with another service: {e.request.url} - Status {e.response.status_code} - Response: {e.response.text}"
        raise HTTPException(status_code=e.response.status_code if e.response.status_code >=400 and e.response.status_code <500 else 502, detail=error_detail)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Network error communicating with another service: {e.request.url} - {str(e)}")
    except HTTPException as e: # Re-raise known HTTPExceptions
        raise e
    except Exception as e:
        # import traceback # For debugging unhandled exceptions
        # print(traceback.format_exc()) # Uncomment for server-side debugging if needed
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")