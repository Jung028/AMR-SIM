# services/putaway_service.py
import random, uuid, time
from datetime import datetime, timedelta
from fastapi import HTTPException
import httpx
from models.putaway_models import PutawayRequest, PutawayHeader, PutawayBody

average_skus_per_order = 5
working_hours = 9

async def fetch_available_skus():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/get-all-skus")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error fetching SKUs")
            data = response.json()
            sku_ids = [sku.get("sku_id") for sku_entry in data.get("skus", [])
                       for sku in sku_entry.get("body", {}).get("sku_list", [])
                       if sku.get("sku_id")]
            return sku_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SKUs: {str(e)}")

async def generate_putaway_order(currentMapId):
    try:
        sku_ids = await fetch_available_skus()
        if not sku_ids:
            raise HTTPException(status_code=404, detail="No available SKUs found")

        try:
            sampled_skus = random.sample(sku_ids, min(len(sku_ids), random.randint(1, average_skus_per_order)))
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Error sampling SKUs: {str(e)}")

        sku_items = []
        for sku_id in sampled_skus:
            try:
                sku_items.append({
                    "sku_code": f"sku{uuid.uuid4().hex[:6].upper()}",
                    "sku_id": sku_id,
                    "in_batch_code": f"batch{random.randint(1, 100)}",
                    "sku_level": random.randint(0, 2),
                    "amount": random.randint(1, 10),
                    "production_date": int(time.time() * 1000) if random.choice([True, False]) else None,
                    "expiration_date": int((datetime.now() + timedelta(days=random.randint(30, 365))).timestamp() * 1000)
                    if random.choice([True, False]) else None
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error generating SKU item: {str(e)}")

        try:
            order = {
                "order_details": {
                    "putaway_order_code": ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8)),
                    "order_type": random.choice([0, 1]),
                    "inbound_wave_code": f"wave_in_{random.randint(2020001, 2029999)}",
                    "owner_code": random.choice(["lidong", "owner2", "owner3"]),
                    "map_id": currentMapId,
                    "print": {
                        "type": random.choice([1, 2]),
                        "content": '[{"field1":"value1"}]'
                    },
                    "carrier": {
                        "type": random.choice([1, 2]),
                        "code": random.choice(["DHL", "UPS", "FedEx"]),
                        "name": random.choice(["DHL Freight", "UPS Express", "FedEx Ground"]),
                        "waybill_code": f"D{random.randint(2020001, 2029999)}"
                    },
                    "dates": {
                        "creation_date": int(time.time() * 1000),
                        "expected_finish_date": int((datetime.now() + timedelta(hours=working_hours)).timestamp() * 1000)
                    },
                    "priority": random.choice([0, 1])
                },
                "sku_items": sku_items
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

        return PutawayRequest(
            header=PutawayHeader(
                warehouse_code="agv-sim",
                user_id="testUser",
                user_key="111111"
            ),
            body=PutawayBody(
                orders=[order]
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
