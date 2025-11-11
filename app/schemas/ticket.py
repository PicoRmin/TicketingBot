"""
Ticket schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.core.enums import TicketCategory, TicketStatus
from app.schemas.user import UserResponse


class TicketBase(BaseModel):
    """Base ticket schema"""
    title: str = Field(..., min_length=3, max_length=200, description="عنوان تیکت")
    description: str = Field(..., min_length=10, description="توضیحات تیکت")
    category: TicketCategory = Field(..., description="دسته‌بندی تیکت")


class TicketCreate(TicketBase):
    """Schema for creating a ticket"""
    pass


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategory] = None
    status: Optional[TicketStatus] = None


class TicketStatusUpdate(BaseModel):
    """Schema for updating ticket status"""
    status: TicketStatus = Field(..., description="وضعیت جدید تیکت")


class TicketResponse(TicketBase):
    """Schema for ticket response"""
    id: int
    ticket_number: str
    status: TicketStatus
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Schema for ticket list response with pagination"""
    items: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

