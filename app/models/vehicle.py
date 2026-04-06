from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, index=True, nullable=False)
    
    unit_number = Column(String, unique=True, index=True) # Örn: ST-104
    license_plate = Column(String, nullable=True)
    vehicle_type = Column(String) # SHUNT_TRUCK, GUEST, SERVICE, CARRIER
    
    is_active = Column(Boolean, default=True)
    current_driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)