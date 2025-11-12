"""
User schemas for request/response validation
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import UserRole, Language
from app.schemas.branch import BranchResponse


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    full_name: str
    language: Language = Language.FA
    branch_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = None
    language: Optional[Language] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    branch_id: Optional[int] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    telegram_chat_id: Optional[str] = None
    branch: Optional[BranchResponse] = None

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user in database (includes password_hash)"""
    password_hash: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class TelegramLinkRequest(BaseModel):
    """Request body for linking Telegram account"""
    chat_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

