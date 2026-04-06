from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, func
import enum
from app.core.database import Base

class TaskStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    PINNED = "PINNED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class ShuntTask(Base):
    __tablename__ = "shunt_tasks"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, index=True, nullable=False)
    
    # Görev detayları
    task_type = Column(String) # PULL, PLUG, PUSH_BACK
    priority = Column(Integer, default=1) # 1-10 arası öncelik
    
    # İlişkiler ve Lokasyon
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=True) # Belirli bir dorse mi?
    from_location = Column(String, nullable=True)
    to_location = Column(String, nullable=True) # Park yeri adı veya genel lokasyon
    to_dock_door_id = Column(Integer, ForeignKey("dock_doors.id"), nullable=True) # Hedef rampa ID
    
    # --- Otomatik Eşleşme Parametreleri ---
    # Eğer trailer_id atanmamışsa, sistem bu kriterlere uyan dorse arar
    req_trailer_type = Column(String, nullable=True)
    req_is_loaded = Column(Boolean, nullable=True)
    req_min_size = Column(Integer, nullable=True)
    
    # Durum Takibi (State Machine)
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    
    # Atamalar
    assigned_driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())