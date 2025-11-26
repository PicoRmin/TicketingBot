"""
Notification feed API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.notification import (
    NotificationResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
)
from app.services.notification_feed_service import (
    list_notifications_for_user,
    mark_all_notifications_as_read,
    mark_notifications_as_read,
)
from app.models import User

router = APIRouter()


@router.get("", response_model=List[NotificationResponse])
def get_my_notifications(
    limit: int = Query(10, ge=1, le=50, description="حداکثر تعداد اعلان بازگشتی"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    دریافت اعلان‌های کاربر جاری
    """
    notifications = list_notifications_for_user(db, current_user.id, limit=limit)
    # Map to response with read flag
    return [
        NotificationResponse(
            id=notif.id,
            title=notif.title,
            body=notif.body,
            severity=notif.severity,
            read=notif.is_read,
            created_at=notif.created_at,
        )
        for notif in notifications
    ]


@router.post("/mark-read", response_model=NotificationMarkReadResponse)
def mark_notifications_read(
    data: NotificationMarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    خوانده‌شدن اعلان‌ها (همه یا لیست خاص)
    """
    if data.notification_ids:
        updated = mark_notifications_as_read(db, current_user.id, data.notification_ids)
    else:
        updated = mark_all_notifications_as_read(db, current_user.id)
    return NotificationMarkReadResponse(updated=updated)

