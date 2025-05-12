from pydantic import BaseModel

# Pydantic model for SKU request
class SKURequest(BaseModel):
    header: dict
    body: dict
