"""
Attachment model for file uploads
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Attachment(Base):
    """Attachment model for ticket file attachments"""
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)  # Stored filename
    original_filename = Column(String, nullable=False)  # Original filename from user
    file_path = Column(String, nullable=False)  # Path to file in storage
    file_size = Column(Integer, nullable=False)  # File size in bytes
    file_type = Column(String, nullable=False)  # MIME type
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_attachment_ticket', 'ticket_id'),
        Index('idx_attachment_uploaded_by', 'uploaded_by_id'),
    )
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', ticket_id={self.ticket_id})>"

