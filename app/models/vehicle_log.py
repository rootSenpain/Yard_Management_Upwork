from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class VehicleDirection(enum.Enum):
    IN = "IN"
    OUT = "OUT"

class VehicleLog(Base):
    __tablename__ = "vehicle_logs"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, index=True)
    trailer_id = Column(Integer, ForeignKey("trailers.id"), nullable=True)
    driver_name = Column(String, nullable=False)
    license_plate = Column(String, nullable=False)
    direction = Column(Enum(VehicleDirection), nullable=False) # IN or OUT
    
    # Hata buradaydı: İsimleri benzersiz (unique) yapıyoruz
    purpose = Column(String, nullable=True) 
    optional_notes = Column(String, nullable=True) 
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships can be added here if needed