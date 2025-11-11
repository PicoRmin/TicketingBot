"""
User schemas for request/response validation
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import UserRole, Language


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    full_name: str
    language: Language = Language.FA


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = None
    language: Optional[Language] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user in database (includes password_hash)"""
    password_hash: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str

