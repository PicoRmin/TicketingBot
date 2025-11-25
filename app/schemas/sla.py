"""
SLA schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.core.enums import TicketPriority, TicketCategory


class SLARuleBase(BaseModel):
    """Base schema for SLA rule"""
    name: str = Field(..., min_length=1, max_length=255, description="نام قانون SLA")
    description: Optional[str] = Field(None, description="توضیحات")
    priority: Optional[TicketPriority] = Field(None, description="اولویت (None = همه)")
    category: Optional[TicketCategory] = Field(None, description="دسته‌بندی (None = همه)")
    department_id: Optional[int] = Field(None, description="دپارتمان (None = همه)")
    response_time_minutes: int = Field(..., ge=1, description="زمان پاسخ هدف (دقیقه)")
    resolution_time_minutes: int = Field(..., ge=1, description="زمان حل هدف (دقیقه)")
    response_warning_minutes: int = Field(default=30, ge=0, description="هشدار قبل از مهلت پاسخ (دقیقه)")
    resolution_warning_minutes: int = Field(default=60, ge=0, description="هشدار قبل از مهلت حل (دقیقه)")
    escalation_enabled: bool = Field(default=False, description="فعال بودن Escalation")
    escalation_after_minutes: Optional[int] = Field(None, ge=1, description="Escalation بعد از این مدت (دقیقه)")
    is_active: bool = Field(default=True, description="وضعیت فعال/غیرفعال")


class SLARuleCreate(SLARuleBase):
    """Schema for creating SLA rule"""
    pass


class SLARuleUpdate(BaseModel):
    """Schema for updating SLA rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    department_id: Optional[int] = None
    response_time_minutes: Optional[int] = Field(None, ge=1)
    resolution_time_minutes: Optional[int] = Field(None, ge=1)
    response_warning_minutes: Optional[int] = Field(None, ge=0)
    resolution_warning_minutes: Optional[int] = Field(None, ge=0)
    escalation_enabled: Optional[bool] = None
    escalation_after_minutes: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class SLARuleResponse(SLARuleBase):
    """Schema for SLA rule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SLALogResponse(BaseModel):
    """Schema for SLA log response"""
    id: int
    ticket_id: int
    sla_rule_id: int
    target_response_time: datetime
    target_resolution_time: datetime
    actual_response_time: Optional[datetime] = None
    actual_resolution_time: Optional[datetime] = None
    response_status: Optional[str] = None
    resolution_status: Optional[str] = None
    escalated: bool
    escalated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Optional related data (برای نمایش در Frontend)
    ticket_number: Optional[str] = None
    sla_rule_name: Optional[str] = None
    
    class Config:
        from_attributes = True


