"""
Telegram Session model for tracking user sessions in Telegram bot
"""
from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TelegramSession(Base):
    """Telegram Session model for tracking active sessions"""
    __tablename__ = "telegram_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    telegram_user_id = Column(Integer, nullable=False, index=True, comment="Telegram user ID")
    token = Column(String(512), nullable=False, comment="JWT access token")
    ip_address = Column(String(64), nullable=True, comment="IP address of the session")
    user_agent = Column(String(255), nullable=True, comment="User agent string")
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, comment="Last activity timestamp")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Session creation timestamp")
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True, comment="Session expiration timestamp")
    is_active = Column(Integer, default=1, nullable=False, comment="1 if active, 0 if logged out")

    # Relationships
    user = relationship("User", back_populates="telegram_sessions")

    # Indexes
    __table_args__ = (
        Index("idx_telegram_sessions_user_active", "user_id", "is_active"),
        Index("idx_telegram_sessions_telegram_user", "telegram_user_id", "is_active"),
        Index("idx_telegram_sessions_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<TelegramSession(id={self.id}, user_id={self.user_id}, telegram_user_id={self.telegram_user_id}, is_active={self.is_active})>"

    def is_expired(self) -> bool:
        """Check if session is expired"""
        if not self.expires_at:
            return True
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Handle both timezone-aware and naive datetimes
        if self.expires_at.tzinfo is None:
            expires = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires = self.expires_at
        return now > expires

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = func.now()

