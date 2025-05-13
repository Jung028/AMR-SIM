from pydantic import BaseModel

class TaskGenerationRequest(BaseModel):
    mode: str  # expected: 'proximity', 'energy', or 'load_balanced'
