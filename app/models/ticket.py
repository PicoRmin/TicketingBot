"""
Ticket model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.enums import TicketCategory, TicketStatus


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_ticket_status', 'status'),
        Index('idx_ticket_category', 'category'),
        Index('idx_ticket_created_at', 'created_at'),
        Index('idx_ticket_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_number='{self.ticket_number}', status='{self.status}')>"

