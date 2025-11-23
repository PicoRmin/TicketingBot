"""
Time Log model for tracking work time on tickets
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TimeLog(Base):
    """Time Log model for tracking work time spent on tickets"""
    __tablename__ = "time_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time tracking
    start_time = Column(DateTime(timezone=True), nullable=False, comment="زمان شروع کار")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="زمان پایان کار")
    duration_minutes = Column(Integer, nullable=True, comment="مدت زمان کار (دقیقه)")
    
    # Description
    description = Column(Text, nullable=True, comment="توضیحات کار انجام شده")
    
    # Status
    is_active = Column(Integer, default=0, nullable=False, comment="آیا در حال کار است (0=خیر، 1=بله)")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_time_log_ticket', 'ticket_id'),
        Index('idx_time_log_user', 'user_id'),
        Index('idx_time_log_active', 'is_active'),
        Index('idx_time_log_ticket_user', 'ticket_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<TimeLog(id={self.id}, ticket_id={self.ticket_id}, user_id={self.user_id}, duration={self.duration_minutes}m)>"

