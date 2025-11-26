"""
Pydantic schemas for notifications
"""
from datetime import datetime
from typing import Optional, Sequence
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: int
    title: str
    body: str
    severity: str = Field(default="info")
    read: bool = Field(default=False)
    created_at: datetime

    class Config:
        orm_mode = True


class NotificationListResponse(BaseModel):
    items: Sequence[NotificationResponse]


class NotificationMarkReadRequest(BaseModel):
    notification_ids: Optional[list[int]] = None


class NotificationMarkReadResponse(BaseModel):
    updated: int

