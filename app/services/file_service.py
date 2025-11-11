"""
File service for file upload/download management
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Attachment, Ticket, User
from app.config import settings
from app.services.ticket_service import can_user_access_ticket


# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES


def validate_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if hasattr(file, 'size') and file.size:
        if file.size > settings.MAX_UPLOAD_SIZE:
            return False, f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)} MB"
    
    # Check file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        return False, f"File type '{file.content_type}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
    
    return True, None


def save_file(file: UploadFile, ticket_id: int, user_id: int) -> Tuple[str, str, int]:
    """
    Save uploaded file to storage
    
    Args:
        file: Uploaded file
        ticket_id: Ticket ID
        user_id: User ID who uploaded the file
        
    Returns:
        Tuple of (stored_filename, file_path, file_size)
    """
    # Create directory for ticket if it doesn't exist
    ticket_dir = settings.UPLOAD_DIR / str(ticket_id)
    ticket_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = ticket_dir / unique_filename
    
    # Read file content
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Check file size again after reading
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)} MB"
        )
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return unique_filename, str(file_path), file_size


def create_attachment(
    db: Session,
    ticket_id: int,
    user_id: int,
    filename: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    file_type: str
) -> Attachment:
    """
    Create attachment record in database
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        user_id: User ID
        filename: Stored filename
        original_filename: Original filename
        file_path: Path to file
        file_size: File size in bytes
        file_type: MIME type
        
    Returns:
        Attachment: Created attachment
    """
    attachment = Attachment(
        ticket_id=ticket_id,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        uploaded_by_id=user_id
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return attachment


def get_attachment(db: Session, attachment_id: int) -> Optional[Attachment]:
    """
    Get attachment by ID
    
    Args:
        db: Database session
        attachment_id: Attachment ID
        
    Returns:
        Attachment or None
    """
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()


def get_ticket_attachments(db: Session, ticket_id: int) -> List[Attachment]:
    """
    Get all attachments for a ticket
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        
    Returns:
        List of attachments
    """
    return db.query(Attachment).filter(Attachment.ticket_id == ticket_id).all()


def delete_attachment_file(file_path: str) -> bool:
    """
    Delete file from storage
    
    Args:
        file_path: Path to file
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def delete_attachment(db: Session, attachment: Attachment) -> bool:
    """
    Delete attachment and its file
    
    Args:
        db: Database session
        attachment: Attachment to delete
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        # Delete file from storage
        delete_attachment_file(attachment.file_path)
        
        # Delete record from database
        db.delete(attachment)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def can_user_access_attachment(user: User, attachment: Attachment, ticket: Ticket) -> bool:
    """
    Check if user can access an attachment
    
    Args:
        user: User trying to access
        attachment: Attachment to access
        ticket: Ticket that attachment belongs to
        
    Returns:
        bool: True if user can access
    """
    # Check if user can access the ticket
    return can_user_access_ticket(user, ticket)

