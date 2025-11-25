"""
Custom Field models for dynamic ticket fields
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Index, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.enums import TicketCategory


from enum import Enum as PyEnum

class CustomFieldType(PyEnum):
    """Types of custom fields"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SELECT = "select"  # Single choice from options
    MULTISELECT = "multiselect"  # Multiple choices from options
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"


class CustomField(Base):
    """
    Custom Field definition model
    Defines a custom field that can be added to tickets
    """
    __tablename__ = "custom_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    label = Column(String(255), nullable=False)  # Display label
    label_en = Column(String(255), nullable=True)  # English label
    field_type = Column(String(50), nullable=False, index=True)  # Stores CustomFieldType.value
    description = Column(Text, nullable=True)
    
    # Field configuration (JSON)
    # For SELECT/MULTISELECT: {"options": [{"value": "opt1", "label": "Option 1"}, ...]}
    # For NUMBER: {"min": 0, "max": 100, "step": 1}
    # For TEXT/TEXTAREA: {"min_length": 0, "max_length": 255, "pattern": "regex"}
    # For DATE/DATETIME: {"min_date": "2024-01-01", "max_date": "2024-12-31"}
    config = Column(SQLiteJSON, nullable=True, comment="Field configuration (JSON)")
    
    # Visibility and scope
    category = Column(Enum(TicketCategory), nullable=True, index=True, comment="Apply to specific category (None = all)")
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Field properties
    is_required = Column(Boolean, default=False, nullable=False)
    is_visible_to_user = Column(Boolean, default=True, nullable=False, comment="Visible in user portal")
    is_editable_by_user = Column(Boolean, default=True, nullable=False, comment="Editable by user in user portal")
    default_value = Column(Text, nullable=True, comment="Default value for new tickets")
    
    # Display settings
    display_order = Column(Integer, default=0, nullable=False, comment="Order in form (lower = first)")
    help_text = Column(Text, nullable=True, comment="Help text shown to users")
    placeholder = Column(String(255), nullable=True, comment="Placeholder text for input fields")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    department = relationship("Department", back_populates="custom_fields")
    branch = relationship("Branch", back_populates="custom_fields")
    values = relationship("TicketCustomFieldValue", back_populates="custom_field", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_custom_field_active', 'is_active'),
        Index('idx_custom_field_category', 'category'),
        Index('idx_custom_field_department', 'department_id'),
        Index('idx_custom_field_branch', 'branch_id'),
        Index('idx_custom_field_type', 'field_type'),
        Index('idx_custom_field_order', 'display_order'),
    )
    
    def __repr__(self):
        return f"<CustomField(id={self.id}, name='{self.name}', type='{self.field_type}')>"


class TicketCustomFieldValue(Base):
    """
    Custom field value for a specific ticket
    Stores the actual value of a custom field for each ticket
    """
    __tablename__ = "ticket_custom_field_values"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    custom_field_id = Column(Integer, ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Value storage (JSON for flexibility)
    # For TEXT/TEXTAREA: string value
    # For NUMBER: number value
    # For DATE/DATETIME: ISO format string
    # For BOOLEAN: true/false
    # For SELECT: single value
    # For MULTISELECT: array of values
    value = Column(SQLiteJSON, nullable=True, comment="Field value (JSON)")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="custom_field_values")
    custom_field = relationship("CustomField", back_populates="values")
    
    # Unique constraint: one value per field per ticket
    __table_args__ = (
        Index('idx_ticket_custom_field', 'ticket_id', 'custom_field_id', unique=True),
        Index('idx_custom_field_value_ticket', 'ticket_id'),
        Index('idx_custom_field_value_field', 'custom_field_id'),
    )
    
    def __repr__(self):
        return f"<TicketCustomFieldValue(id={self.id}, ticket_id={self.ticket_id}, field_id={self.custom_field_id})>"

