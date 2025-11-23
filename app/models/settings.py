"""
System settings model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class SystemSettings(Base):
    """System-wide settings stored in database"""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String, default="string")  # string, int, bool, json
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by_id = Column(Integer, nullable=True)  # User who updated this setting

    def __repr__(self):
        return f"<SystemSettings(key='{self.key}', value='{self.value}')>"

