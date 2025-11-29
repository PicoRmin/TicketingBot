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


class GeneralSettingsResponse(BaseModel):
    """General settings response - includes telegram bot and other settings"""
    telegram_bot_token: Optional[str] = None
    telegram_bot_enabled: bool = False
    telegram_bot_started: bool = False
    auto_start_bot: bool = False
    send_ticket_notifications: bool = True
    send_status_updates: bool = True
    send_sla_warnings: bool = True
    send_resolution_notifications: bool = True
    notification_language: str = "auto"
    welcome_message_enabled: bool = True
    welcome_message_text: Optional[str] = None
    help_command_enabled: bool = True
    help_command_text: Optional[str] = None

    class Config:
        from_attributes = True


class GeneralSettingsUpdate(BaseModel):
    """General settings update request"""
    telegram_bot_token: Optional[str] = None
    telegram_bot_enabled: Optional[bool] = None
    auto_start_bot: Optional[bool] = None
    send_ticket_notifications: Optional[bool] = None
    send_status_updates: Optional[bool] = None
    send_sla_warnings: Optional[bool] = None
    send_resolution_notifications: Optional[bool] = None
    notification_language: Optional[str] = None
    welcome_message_enabled: Optional[bool] = None
    welcome_message_text: Optional[str] = None
    help_command_enabled: Optional[bool] = None
    help_command_text: Optional[str] = None
