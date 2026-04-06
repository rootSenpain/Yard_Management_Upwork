from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum
from app.core.database import Base

# Define the 7 roles requested by the client
class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    SUPER_USER = "Super User"
    DISPATCH = "Dispatch"
    WAREHOUSE = "Warehouse"
    GATEHOUSE = "Gatehouse"
    DRIVER = "Driver"
    REPORTING = "Reporting"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Never store passwords as plain text!
    hashed_password = Column(String, nullable=False)
    # Default role is DRIVER if not specified
    role = Column(Enum(UserRole), default=UserRole.DRIVER, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Required for multi-tenant isolation across different logistic sites
    region_id = Column(Integer, index=True, nullable=False)