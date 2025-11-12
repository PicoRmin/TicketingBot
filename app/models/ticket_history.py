"""Ticket history model"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.core.enums import TicketStatus


class TicketHistory(Base):
    """Track ticket status changes and comments."""
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(TicketStatus), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    ticket = relationship("Ticket", back_populates="history")
    changed_by = relationship("User", backref="changed_ticket_history")

    def __repr__(self) -> str:
        return f"<TicketHistory(id={self.id}, ticket_id={self.ticket_id}, status={self.status})>"
