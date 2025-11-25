"""
Ticket model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.enums import TicketCategory, TicketStatus, TicketPriority


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    estimated_resolution_hours = Column(Integer, nullable=True)
    actual_resolution_hours = Column(Integer, nullable=True)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5
    satisfaction_comment = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)  # زمان اولین پاسخ
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tickets")
    department = relationship("Department", back_populates="tickets")
    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketHistory.created_at")
    sla_logs = relationship("SLALog", back_populates="ticket", cascade="all, delete-orphan")
    time_logs = relationship("TimeLog", back_populates="ticket", cascade="all, delete-orphan", order_by="TimeLog.start_time")
    custom_field_values = relationship("TicketCustomFieldValue", back_populates="ticket", cascade="all, delete-orphan")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_ticket_status', 'status'),
        Index('idx_ticket_category', 'category'),
        Index('idx_ticket_priority', 'priority'),
        Index('idx_ticket_created_at', 'created_at'),
        Index('idx_ticket_user_status', 'user_id', 'status'),
        Index('idx_ticket_branch', 'branch_id'),
        Index('idx_ticket_department', 'department_id'),
        Index('idx_ticket_assigned', 'assigned_to_id'),
        Index('idx_ticket_status_priority', 'status', 'priority'),
    )
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_number='{self.ticket_number}', status='{self.status}')>"

