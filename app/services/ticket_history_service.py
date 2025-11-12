"""Ticket history service"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import TicketHistory
from app.schemas.ticket_history import TicketHistoryCreate


def create_ticket_history(db: Session, data: TicketHistoryCreate) -> TicketHistory:
    """Create a history entry for a ticket."""
    history = TicketHistory(
        ticket_id=data.ticket_id,
        status=data.status,
        changed_by_id=data.changed_by_id,
        comment=data.comment,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_ticket_history(db: Session, ticket_id: int) -> List[TicketHistory]:
    """Return ordered history for a ticket."""
    return (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.created_at.asc())
        .all()
    )
