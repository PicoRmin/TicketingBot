"""
Settings schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FileSettingsResponse(BaseModel):
    """File settings response"""
    max_images_per_ticket: int = Field(..., description="حداکثر تعداد عکس در هر تیکت")
    max_documents_per_ticket: int = Field(..., description="حداکثر تعداد فایل متنی در هر تیکت")
    max_file_size_mb: int = Field(..., description="حداکثر اندازه فایل به مگابایت")
    allowed_image_types: List[str] = Field(..., description="انواع فایل تصویری مجاز")
    allowed_document_types: List[str] = Field(..., description="انواع فایل متنی مجاز")

    class Config:
        from_attributes = True


class FileSettingsUpdate(BaseModel):
    """File settings update request"""
    max_images_per_ticket: Optional[int] = Field(None, ge=1, le=50, description="حداکثر تعداد عکس")
    max_documents_per_ticket: Optional[int] = Field(None, ge=1, le=50, description="حداکثر تعداد فایل متنی")
    max_file_size_mb: Optional[int] = Field(None, ge=1, le=100, description="حداکثر اندازه فایل (MB)")
    allowed_image_types: Optional[List[str]] = Field(None, description="انواع فایل تصویری مجاز")
    allowed_document_types: Optional[List[str]] = Field(None, description="انواع فایل متنی مجاز")


class SettingsResponse(BaseModel):
    """All settings response"""
    file_settings: FileSettingsResponse

    class Config:
        from_attributes = True

