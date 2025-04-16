from fastapi import FastAPI, HTTPException, Query
from models.sku_sync import SKUSyncRequest

app = FastAPI()

@app.post("/api/inventory/sync")
async def sku_sync(request: SKUSyncRequest, warehouse_code: str = Query(...), owner_code: str = Query(...)):
    # You can use the 'warehouse_code' and 'owner_code' for additional validation or logging if needed.
    # Here, we simply return the received data for confirmation that it was parsed correctly.

    # For example, print out the request data for debugging:
    print(request.dict())

    # Implement your business logic here (e.g., syncing the SKU information with a database or external service).
    
    return {"message": "SKU Sync request received", "status": "success"}
