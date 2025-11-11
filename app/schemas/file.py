"""
File schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FileResponse(BaseModel):
    """Schema for file response"""
    id: int
    ticket_id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    uploaded_by_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    ticket_id: int
    message: str = "File uploaded successfully"

