from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base

class DockDoor(Base):
    __tablename__ = "dock_doors"

    id = Column(Integer, primary_key=True, index=True)
    door_number = Column(String, index=True, nullable=False)
    region_id = Column(Integer, index=True, nullable=False)
    
    # Rampa durumu
    is_active = Column(Boolean, default=True)
    is_occupied = Column(Boolean, default=False)
    
    # Şu an bu rampada olan dorse (opsiyonel)
    current_trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=True)