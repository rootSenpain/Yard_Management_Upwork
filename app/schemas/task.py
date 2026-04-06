from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus

class TaskBase(BaseModel):
    task_type: str # PULL, PLUG, PUSH_BACK
    priority: int = 1
    trailer_id: Optional[int] = None
    from_location: str
    to_location: str
    to_dock_door_id: Optional[int] = None
    
    # Parametre bazlı eşleşme için
    req_trailer_type: Optional[str] = None
    req_is_loaded: Optional[bool] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    assigned_driver_id: Optional[int] = None
    region_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)