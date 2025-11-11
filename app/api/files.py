"""
File API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import os
from app.database import get_db
from app.models import Attachment, Ticket, User
from app.schemas.file import FileResponse, FileUploadResponse
from app.api.deps import get_current_active_user, require_admin
from app.services.file_service import (
    validate_file,
    save_file,
    create_attachment,
    get_attachment,
    get_ticket_attachments,
    delete_attachment,
    can_user_access_attachment,
)
from app.services.ticket_service import get_ticket, can_user_access_ticket

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    ticket_id: int = Query(..., description="شناسه تیکت"),
    file: UploadFile = File(..., description="فایل برای آپلود"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file and attach it to a ticket
    
    Args:
        ticket_id: Ticket ID to attach file to
        file: File to upload
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        FileUploadResponse: Uploaded file information
        
    Raises:
        HTTPException: If ticket not found, access denied, or file validation fails
    """
    # Check if ticket exists
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check access to ticket
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this ticket"
        )
    
    # Validate file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    try:
        # Save file
        filename, file_path, file_size = save_file(file, ticket_id, current_user.id)
        
        # Create attachment record
        attachment = create_attachment(
            db=db,
            ticket_id=ticket_id,
            user_id=current_user.id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.content_type or "application/octet-stream"
        )
        
        return FileUploadResponse(
            id=attachment.id,
            filename=attachment.filename,
            original_filename=attachment.original_filename,
            file_size=attachment.file_size,
            file_type=attachment.file_type,
            ticket_id=attachment.ticket_id,
            message="File uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/{file_id}", response_class=FastAPIFileResponse)
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a file
    
    Args:
        file_id: File ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        FileResponse: File to download
        
    Raises:
        HTTPException: If file not found or access denied
    """
    attachment = get_attachment(db, file_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get ticket to check access
    ticket = get_ticket(db, attachment.ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check access
    if not can_user_access_attachment(current_user, attachment, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this file"
        )
    
    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    return FastAPIFileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.file_type
    )


@router.get("/ticket/{ticket_id}/list", response_model=List[FileResponse])
async def get_ticket_files(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all files attached to a ticket
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[FileResponse]: List of files
        
    Raises:
        HTTPException: If ticket not found or access denied
    """
    # Check if ticket exists
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this ticket"
        )
    
    attachments = get_ticket_attachments(db, ticket_id)
    return attachments


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a file (Admin only)
    
    Args:
        file_id: File ID
        db: Database session
        current_user: Current admin user
        
    Raises:
        HTTPException: If file not found
    """
    attachment = get_attachment(db, file_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    success = delete_attachment(db, attachment)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

