"""
SLA (Service Level Agreement) model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.enums import TicketPriority, TicketCategory


class SLARule(Base):
    """SLA Rule model for defining service level agreements"""
    __tablename__ = "sla_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Rule conditions
    priority = Column(Enum(TicketPriority), nullable=True, index=True)  # None = all priorities
    category = Column(Enum(TicketCategory), nullable=True, index=True)  # None = all categories
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # SLA targets (in minutes)
    response_time_minutes = Column(Integer, nullable=False, comment="زمان پاسخ هدف (دقیقه)")
    resolution_time_minutes = Column(Integer, nullable=False, comment="زمان حل هدف (دقیقه)")
    
    # Warning thresholds (in minutes before deadline)
    response_warning_minutes = Column(Integer, default=30, nullable=False, comment="هشدار قبل از مهلت پاسخ (دقیقه)")
    resolution_warning_minutes = Column(Integer, default=60, nullable=False, comment="هشدار قبل از مهلت حل (دقیقه)")
    
    # Escalation
    escalation_enabled = Column(Boolean, default=False, nullable=False)
    escalation_after_minutes = Column(Integer, nullable=True, comment="Escalation بعد از این مدت (دقیقه)")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="sla_rules")
    sla_logs = relationship("SLALog", back_populates="sla_rule", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_sla_priority_category', 'priority', 'category'),
        Index('idx_sla_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<SLARule(id={self.id}, name='{self.name}', priority={self.priority}, response={self.response_time_minutes}m, resolution={self.resolution_time_minutes}m)>"


class SLALog(Base):
    """SLA Log model for tracking SLA compliance"""
    __tablename__ = "sla_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sla_rule_id = Column(Integer, ForeignKey("sla_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Target times
    target_response_time = Column(DateTime(timezone=True), nullable=False, comment="مهلت پاسخ")
    target_resolution_time = Column(DateTime(timezone=True), nullable=False, comment="مهلت حل")
    
    # Actual times
    actual_response_time = Column(DateTime(timezone=True), nullable=True, comment="زمان واقعی پاسخ")
    actual_resolution_time = Column(DateTime(timezone=True), nullable=True, comment="زمان واقعی حل")
    
    # Status
    response_status = Column(String(20), nullable=True, comment="on_time, warning, breached")
    resolution_status = Column(String(20), nullable=True, comment="on_time, warning, breached")
    
    # Escalation
    escalated = Column(Boolean, default=False, nullable=False)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="sla_logs")
    sla_rule = relationship("SLARule", back_populates="sla_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_sla_log_ticket', 'ticket_id'),
        Index('idx_sla_log_status', 'response_status', 'resolution_status'),
        Index('idx_sla_log_escalated', 'escalated'),
    )
    
    def __repr__(self):
        return f"<SLALog(id={self.id}, ticket_id={self.ticket_id}, response_status={self.response_status}, resolution_status={self.resolution_status})>"


