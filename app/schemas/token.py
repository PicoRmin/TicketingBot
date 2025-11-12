"""
Token schemas for authentication
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema for access token response"""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    branch_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """Schema for requesting a new access token using refresh token"""
    refresh_token: str

