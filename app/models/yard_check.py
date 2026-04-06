from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
import enum
from app.core.database import Base

class AuditStatus(str, enum.Enum):
    VERIFIED = "Verified"
    FIXED = "Fixed"
    MISSING = "Missing"

class YardCheck(Base):
    __tablename__ = "yard_checks"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, index=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String, default="In-Progress") # In-Progress, Completed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class YardCheckItem(Base):
    __tablename__ = "yard_check_items"

    id = Column(Integer, primary_key=True, index=True)
    yard_check_id = Column(Integer, ForeignKey("yard_checks.id"))
    trailer_id = Column(Integer, ForeignKey("trailers.id"))
    
    status = Column(Enum(AuditStatus))
    notes = Column(String, nullable=True)
    
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())