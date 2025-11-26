"""
Notification model for in-app/mobile feeds
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    """Stores per-user feed notifications (in-app/mobile)"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="info")
    # NOTE:
    #   Attribute name "metadata" is reserved by SQLAlchemy's Declarative API.
    #   We keep the underlying column name as "metadata" for compatibility,
    #   but expose it on the model as "extra".
    extra = Column("metadata", JSON, nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="notifications")

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, severity='{self.severity}')>"

