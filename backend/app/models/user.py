# ASSIGNED TO: BE-1
# Pydantic models for User
# Schemas needed:
# - UserCreate: name, email, password
# - UserLogin: email, password
# - UserResponse: user_id, name, email, subscription_type (no password)
# - UserInDB: all fields including hashed_password

from pydantic import BaseModel, EmailStr
from typing import Optional

# TODO: Define User models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    subscription_type: Optional[str] = "free"
