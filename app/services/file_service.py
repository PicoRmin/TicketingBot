"""
File service for file upload/download management
"""
import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Attachment, Ticket, User
from app.config import settings
from app.services.ticket_service import can_user_access_ticket
from app.services.settings_service import get_file_settings

logger = logging.getLogger(__name__)


# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES


def validate_file_count(
    db: Session,
    ticket_id: int,
    file_type: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate file count limits for a ticket
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        file_type: MIME type of the file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        file_settings = get_file_settings(db)
        
        # Get existing attachments
        existing_attachments = get_ticket_attachments(db, ticket_id)
        
        # Count images and documents
        image_count = sum(1 for att in existing_attachments if att.file_type in ALLOWED_IMAGE_TYPES)
        document_count = sum(1 for att in existing_attachments if att.file_type in ALLOWED_DOCUMENT_TYPES)
        
        # Check if new file is image or document
        is_image = file_type in ALLOWED_IMAGE_TYPES
        is_document = file_type in ALLOWED_DOCUMENT_TYPES
        
        if is_image:
            if image_count >= file_settings["max_images_per_ticket"]:
                logger.warning(f"File count limit exceeded for ticket {ticket_id}: {image_count}/{file_settings['max_images_per_ticket']} images")
                return False, f"حداکثر {file_settings['max_images_per_ticket']} عکس در هر تیکت مجاز است. شما قبلاً {image_count} عکس آپلود کرده‌اید."
        elif is_document:
            if document_count >= file_settings["max_documents_per_ticket"]:
                logger.warning(f"File count limit exceeded for ticket {ticket_id}: {document_count}/{file_settings['max_documents_per_ticket']} documents")
                return False, f"حداکثر {file_settings['max_documents_per_ticket']} فایل متنی در هر تیکت مجاز است. شما قبلاً {document_count} فایل متنی آپلود کرده‌اید."
        
        return True, None
    except Exception as e:
        logger.error(f"Error validating file count for ticket {ticket_id}: {e}", exc_info=True)
        # Fail open - allow upload if validation fails
        return True, None


def validate_file(file: UploadFile, db: Session = None, ticket_id: int = None) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file
        db: Database session (optional, for file count validation)
        ticket_id: Ticket ID (optional, for file count validation)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get file settings
    if db:
        file_settings = get_file_settings(db)
        max_size = file_settings["max_file_size_mb"] * 1024 * 1024
        allowed_types = set(file_settings["allowed_image_types"] + file_settings["allowed_document_types"])
    else:
        max_size = settings.MAX_UPLOAD_SIZE
        allowed_types = ALLOWED_FILE_TYPES
    
    # Check file size
    if hasattr(file, 'size') and file.size:
        if file.size > max_size:
            max_size_mb = max_size / (1024*1024)
            file_size_mb = file.size / (1024*1024)
            return False, f"حجم فایل ({file_size_mb:.2f} مگابایت) بیش از حد مجاز ({max_size_mb} مگابایت) است."
    
    # Check file type
    if file.content_type not in allowed_types:
        allowed_types_str = ', '.join(sorted(allowed_types))
        return False, f"نوع فایل '{file.content_type}' مجاز نیست. انواع مجاز: {allowed_types_str}"
    
    # Check file count if db and ticket_id provided
    if db and ticket_id:
        is_valid, error_msg = validate_file_count(db, ticket_id, file.content_type)
        if not is_valid:
            return False, error_msg
    
    return True, None


def save_file(file: UploadFile, ticket_id: int, user_id: int, db: Session = None) -> Tuple[str, str, int]:
    """
    Save uploaded file to storage
    
    Args:
        file: Uploaded file
        ticket_id: Ticket ID
        user_id: User ID who uploaded the file
        db: Database session (optional, for getting file settings)
        
    Returns:
        Tuple of (stored_filename, file_path, file_size)
        
    Raises:
        HTTPException: If file size exceeds limit or save fails
    """
    try:
        # Get max file size from settings if db provided
        if db:
            file_settings = get_file_settings(db)
            max_size = file_settings["max_file_size_mb"] * 1024 * 1024
        else:
            max_size = settings.MAX_UPLOAD_SIZE
        
        # Create directory for ticket if it doesn't exist
        ticket_dir = settings.UPLOAD_DIR / str(ticket_id)
        ticket_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created/verified directory for ticket {ticket_id}: {ticket_dir}")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = ticket_dir / unique_filename
        
        # Read file content
        file_content = file.file.read()
        file_size = len(file_content)
        logger.debug(f"Read file content: {file_size} bytes for ticket {ticket_id}")
        
        # Check file size again after reading
        if file_size > max_size:
            max_size_mb = max_size / (1024*1024)
            file_size_mb = file_size / (1024*1024)
            logger.warning(f"File size exceeded for ticket {ticket_id}: {file_size_mb:.2f} MB > {max_size_mb} MB")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"حجم فایل ({file_size_mb:.2f} مگابایت) بیش از حد مجاز ({max_size_mb} مگابایت) است."
            )
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"File saved successfully: {unique_filename} ({file_size} bytes) for ticket {ticket_id} by user {user_id}")
        return unique_filename, str(file_path), file_size
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving file for ticket {ticket_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


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
    try:
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
        
        logger.debug(f"Attachment record created: id={attachment.id}, ticket_id={ticket_id}, filename={filename}")
        return attachment
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating attachment record for ticket {ticket_id}: {e}", exc_info=True)
        raise


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
        file_path = attachment.file_path
        attachment_id = attachment.id
        ticket_id = attachment.ticket_id
        
        # Delete file from storage
        file_deleted = delete_attachment_file(file_path)
        if not file_deleted:
            logger.warning(f"File not found or could not be deleted: {file_path} (attachment {attachment_id})")
            # Continue with database deletion even if file is missing
        
        # Delete record from database
        db.delete(attachment)
        db.commit()
        
        logger.info(f"Attachment {attachment_id} deleted successfully (ticket {ticket_id}, file deleted: {file_deleted})")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting attachment {attachment.id}: {e}", exc_info=True)
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

