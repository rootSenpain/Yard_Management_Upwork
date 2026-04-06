from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Shared properties
class TrailerBase(BaseModel):
    region_id: int
    trailer_number: str
    status: Optional[str] = "GATED_IN"
    is_loaded: Optional[bool] = False

# Properties to receive on creation
class TrailerCreate(TrailerBase):
    pass

# Properties to return to client (Response)
class TrailerResponse(TrailerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # This config allows Pydantic to read data from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)