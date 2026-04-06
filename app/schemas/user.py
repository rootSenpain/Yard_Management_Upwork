from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.models.user import UserRole

# Properties to receive on user registration
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.DRIVER
    region_id: int

# Properties to return to client
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    region_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

# Standard OAuth2 Token format
class Token(BaseModel):
    access_token: str
    token_type: str