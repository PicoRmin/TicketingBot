from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BranchBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    code: str = Field(..., max_length=50)
    address: Optional[str] = Field(None, max_length=512)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=512)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class BranchResponse(BranchBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

