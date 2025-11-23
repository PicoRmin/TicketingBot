"""
Department schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DepartmentBase(BaseModel):
    """Base schema for department"""
    name: str = Field(..., min_length=1, max_length=255, description="نام دپارتمان")
    name_en: Optional[str] = Field(None, max_length=255, description="نام انگلیسی دپارتمان")
    code: str = Field(..., min_length=1, max_length=50, description="کد دپارتمان")
    description: Optional[str] = Field(None, description="توضیحات")
    is_active: bool = Field(default=True, description="وضعیت فعال/غیرفعال")


class DepartmentCreate(DepartmentBase):
    """Schema for creating department"""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_en: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Schema for department response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

