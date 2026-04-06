from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Trailer(Base):
    __tablename__ = "trailers"

    id = Column(Integer, primary_key=True, index=True)
    # Multi-tenant design: data isolation across sites
    region_id = Column(Integer, index=True, nullable=False)
    
    trailer_number = Column(String, unique=True, index=True, nullable=False)
    
    # Algoritma için yeni eklenen özellikler
    trailer_type = Column(String, nullable=True)  # Örn: DRY_VAN, REEFER, FLATBED
    size = Column(Integer, nullable=True)         # Örn: 53, 48 (feet)
    shipping_line = Column(String, nullable=True) # Örn: Maersk, DHL, MSC
    
    status = Column(String, default="GATED_IN")   # GATED_IN, AT_DOOR, IN_YARD
    is_loaded = Column(Boolean, default=False)
    
    # Tracking timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())