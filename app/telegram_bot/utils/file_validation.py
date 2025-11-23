"""
File validation utilities for Telegram bot
"""
from typing import Tuple, Optional, Dict, Any
from app.config import settings
from app.services.file_service import ALLOWED_FILE_TYPES, ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES


def validate_telegram_file(
    file_size: Optional[int],
    mime_type: Optional[str],
    file_name: Optional[str] = None,
    file_settings: Optional[Dict[str, Any]] = None,
    ticket_attachments_count: Optional[Dict[str, int]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate file from Telegram before uploading
    
    Args:
        file_size: File size in bytes (from Telegram file object)
        mime_type: MIME type of the file
        file_name: Optional file name for extension checking
        file_settings: Optional file settings from API (if None, uses defaults from config)
        ticket_attachments_count: Optional dict with image_count and document_count
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Use settings from API if provided, otherwise use config defaults
    if file_settings:
        max_size_bytes = file_settings.get("max_file_size_mb", 10) * 1024 * 1024
        # Handle both list and string formats
        image_types = file_settings.get("allowed_image_types", [])
        if isinstance(image_types, str):
            allowed_image_types = set(image_types.split(","))
        else:
            allowed_image_types = set(image_types) if image_types else set()
        
        doc_types = file_settings.get("allowed_document_types", [])
        if isinstance(doc_types, str):
            allowed_document_types = set(doc_types.split(","))
        else:
            allowed_document_types = set(doc_types) if doc_types else set()
        
        allowed_types = allowed_image_types | allowed_document_types
        max_images = file_settings.get("max_images_per_ticket", 10)
        max_documents = file_settings.get("max_documents_per_ticket", 5)
    else:
        # Fallback to config defaults
        max_size_bytes = settings.MAX_UPLOAD_SIZE
        allowed_types = ALLOWED_FILE_TYPES
        allowed_image_types = ALLOWED_IMAGE_TYPES
        allowed_document_types = ALLOWED_DOCUMENT_TYPES
        max_images = 10
        max_documents = 5
    
    # Check file size
    if file_size and file_size > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        file_size_mb = file_size / (1024 * 1024)
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size of {max_size_mb} MB"
    
    # Check MIME type
    if mime_type and mime_type not in allowed_types:
        # Try to check by file extension if MIME type is not recognized
        if file_name:
            file_ext = file_name.lower().split('.')[-1] if '.' in file_name else ''
            # Common extensions mapping
            ext_to_mime = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt': 'text/plain',
            }
            mapped_mime = ext_to_mime.get(file_ext)
            if mapped_mime and mapped_mime in allowed_types:
                mime_type = mapped_mime  # Update mime_type for count check
            else:
                allowed_types_str = ', '.join(sorted(allowed_types))
                return False, f"File type '{mime_type}' is not allowed. Allowed types: {allowed_types_str}"
    
    # Check file count limits if ticket_attachments_count provided
    if ticket_attachments_count and file_settings:
        is_image = mime_type in allowed_image_types
        is_document = mime_type in allowed_document_types
        
        if is_image:
            current_count = ticket_attachments_count.get("image_count", 0)
            if current_count >= max_images:
                return False, f"Maximum {max_images} images allowed per ticket. You have already uploaded {current_count} images."
        elif is_document:
            current_count = ticket_attachments_count.get("document_count", 0)
            if current_count >= max_documents:
                return False, f"Maximum {max_documents} documents allowed per ticket. You have already uploaded {current_count} documents."
    
    return True, None

