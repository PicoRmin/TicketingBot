"""
Ticket schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.core.enums import TicketCategory, TicketStatus, TicketPriority
from app.schemas.user import UserResponse


class TicketBase(BaseModel):
    """Base ticket schema"""
    title: str = Field(..., min_length=3, max_length=200, description="عنوان تیکت")
    description: str = Field(..., min_length=10, description="توضیحات تیکت")
    category: TicketCategory = Field(..., description="دسته‌بندی تیکت")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM, description="اولویت تیکت")


class TicketCreate(TicketBase):
    """Schema for creating a ticket"""
    branch_id: Optional[int] = Field(None, description="شناسه شعبه")
    department_id: Optional[int] = Field(None, description="شناسه دپارتمان")


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategory] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    department_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    estimated_resolution_hours: Optional[int] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5, description="رضایت‌مندی (1-5)")
    satisfaction_comment: Optional[str] = None
    cost: Optional[Decimal] = None


class TicketStatusUpdate(BaseModel):
    """Schema for updating ticket status"""
    status: TicketStatus = Field(..., description="وضعیت جدید تیکت")
    comment: Optional[str] = Field(
        None,
        description="توضیح یا یادداشت تکمیلی درباره تغییر وضعیت",
        min_length=1,
    )
    is_internal: bool = Field(
        True,
        description="مشخص می‌کند آیا توضیح صرفاً برای داخل سیستم باشد یا برای کاربر نهایی هم قابل دیدن است",
    )


class TicketAssignUpdate(BaseModel):
    """Schema for assigning ticket to a specialist"""
    assigned_to_id: int = Field(..., description="شناسه کارشناس مسئول")


class BulkActionRequest(BaseModel):
    """Schema for bulk actions on tickets"""
    ticket_ids: List[int] = Field(..., min_items=1, description="لیست شناسه تیکت‌ها")
    action: str = Field(..., description="نوع عملیات: status, assign, unassign, delete")
    status: Optional[TicketStatus] = Field(None, description="وضعیت جدید (برای action=status)")
    assigned_to_id: Optional[int] = Field(None, description="شناسه کارشناس (برای action=assign)")


class BulkActionResponse(BaseModel):
    """Schema for bulk action response"""
    success_count: int = Field(..., description="تعداد تیکت‌های موفق")
    failed_count: int = Field(..., description="تعداد تیکت‌های ناموفق")
    failed_ids: List[int] = Field(default_factory=list, description="لیست شناسه تیکت‌های ناموفق")


class TicketResponse(TicketBase):
    """Schema for ticket response"""
    id: int
    ticket_number: str
    status: TicketStatus
    user_id: int
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    estimated_resolution_hours: Optional[int] = None
    actual_resolution_hours: Optional[int] = None
    satisfaction_rating: Optional[int] = None
    satisfaction_comment: Optional[str] = None
    cost: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    first_response_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    assigned_to: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Schema for ticket list response with pagination"""
    items: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
