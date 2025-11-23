"""
Time Log schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TimeLogBase(BaseModel):
    """Base schema for Time Log"""
    ticket_id: int = Field(..., description="شناسه تیکت")
    description: Optional[str] = Field(None, description="توضیحات کار انجام شده")


class TimeLogCreate(TimeLogBase):
    """Schema for creating Time Log"""
    pass


class TimeLogUpdate(BaseModel):
    """Schema for updating Time Log"""
    description: Optional[str] = Field(None, description="توضیحات کار انجام شده")


class TimeLogResponse(TimeLogBase):
    """Schema for Time Log response"""
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    user: Optional[dict] = None
    ticket: Optional[dict] = None
    
    class Config:
        from_attributes = True


class TimeLogSummary(BaseModel):
    """Schema for Time Log summary"""
    total_minutes: int
    total_hours: float
    logs_count: int

