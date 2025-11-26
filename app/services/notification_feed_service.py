"""
Service helpers for persistent in-app/mobile notifications
"""
from typing import Iterable, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notification import Notification


def create_notifications(
    db: Session,
    notifications: Iterable[dict],
) -> List[Notification]:
    """
    Persist multiple notifications at once.

    Args:
        db: Database session
        notifications: Iterable of dicts with keys (user_id, title, body, severity, metadata/extra)
    """
    entries: List[Notification] = []
    for payload in notifications:
        user_id = payload.get("user_id")
        title = (payload.get("title") or "").strip()
        body = (payload.get("body") or "").strip()
        if not user_id or not title or not body:
            continue
        entry = Notification(
            user_id=user_id,
            title=title[:255],
            body=body,
            severity=payload.get("severity") or "info",
            # "metadata" key is kept for backwards compatibility; it is
            # mapped to the "extra" model attribute which stores JSON
            # in the "metadata" DB column.
            extra=payload.get("extra") or payload.get("metadata"),
        )
        entries.append(entry)

    if not entries:
        return []

    try:
        db.add_all(entries)
        db.commit()
        for entry in entries:
            db.refresh(entry)
        return entries
    except Exception:
        db.rollback()
        raise


def list_notifications_for_user(db: Session, user_id: int, limit: int = 20) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def mark_notifications_as_read(
    db: Session,
    user_id: int,
    notification_ids: Optional[List[int]] = None,
) -> int:
    query = db.query(Notification).filter(Notification.user_id == user_id, Notification.read_at.is_(None))
    if notification_ids:
        query = query.filter(Notification.id.in_(notification_ids))
    updated = query.update(
        {
            Notification.read_at: func.now(),
            Notification.updated_at: func.now(),
        },
        synchronize_session=False,
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return updated


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    return mark_notifications_as_read(db, user_id, None)

