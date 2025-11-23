"""
Automation Rule model for auto-assignment and other automation
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.enums import TicketPriority, TicketCategory, UserRole


class AutomationRule(Base):
    """Automation Rule model for defining auto-assignment and automation rules"""
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Rule type
    rule_type = Column(String(50), nullable=False, index=True, comment="auto_assign, auto_close, auto_notify")
    
    # Conditions (JSON for flexibility)
    conditions = Column(SQLiteJSON, nullable=True, comment="شرایط فعال شدن قانون (JSON)")
    # Example: {"priority": "high", "category": "internet", "department_id": 1}
    
    # Actions (JSON for flexibility)
    actions = Column(SQLiteJSON, nullable=False, comment="اقدامات (JSON)")
    # For auto_assign: {"assign_to_user_id": 1} or {"assign_to_department_id": 1, "round_robin": true}
    # For auto_close: {"close_after_hours": 48, "only_if_resolved": true}
    # For auto_notify: {"notify_users": [1, 2], "notify_roles": ["admin"], "message": "..."}
    
    # Priority and order
    priority = Column(Integer, default=100, nullable=False, comment="اولویت اجرا (کمتر = اولویت بالاتر)")
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_automation_type_active', 'rule_type', 'is_active'),
        Index('idx_automation_priority', 'priority'),
    )
    
    def __repr__(self):
        return f"<AutomationRule(id={self.id}, name='{self.name}', type='{self.rule_type}', priority={self.priority})>"

