"""Ticket history schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import TicketStatus


class TicketHistoryBase(BaseModel):
    """Shared fields for ticket history."""
    status: TicketStatus = Field(..., description="وضعیت تیکت پس از تغییر")
    comment: Optional[str] = Field(None, description="توضیح یا یادداشت")


class TicketHistoryCreate(TicketHistoryBase):
    """Payload for creating history records."""
    ticket_id: int
    changed_by_id: Optional[int] = None


class TicketHistoryResponse(TicketHistoryBase):
    """Response model for ticket history."""
    id: int
    ticket_id: int
    changed_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
