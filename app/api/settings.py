"""
Settings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.settings import (
    FileSettingsResponse, 
    FileSettingsUpdate, 
    SettingsResponse,
    GeneralSettingsResponse,
    GeneralSettingsUpdate
)
from app.api.deps import get_current_active_user, require_central_admin
from app.services.settings_service import (
    get_file_settings,
    set_setting,
    get_all_settings,
    initialize_default_settings
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.get("/file", response_model=FileSettingsResponse)
async def get_file_settings_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get file upload settings"""
    lang = resolve_lang(request, current_user)
    
    # Initialize defaults if needed
    initialize_default_settings(db)
    
    settings = get_file_settings(db)
    return FileSettingsResponse(**settings)


@router.put("/file", response_model=FileSettingsResponse)
async def update_file_settings(
    request: Request,
    settings_data: FileSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_central_admin)
):
    """Update file upload settings (Central Admin only)"""
    lang = resolve_lang(request, current_user)
    
    # Get current settings
    current_settings = get_file_settings(db)
    
    # Update settings
    if settings_data.max_images_per_ticket is not None:
        set_setting(
            db,
            "max_images_per_ticket",
            str(settings_data.max_images_per_ticket),
            value_type="int",
            description="حداکثر تعداد عکس در هر تیکت",
            updated_by_id=current_user.id
        )
    
    if settings_data.max_documents_per_ticket is not None:
        set_setting(
            db,
            "max_documents_per_ticket",
            str(settings_data.max_documents_per_ticket),
            value_type="int",
            description="حداکثر تعداد فایل متنی در هر تیکت",
            updated_by_id=current_user.id
        )
    
    if settings_data.max_file_size_mb is not None:
        set_setting(
            db,
            "max_file_size_mb",
            str(settings_data.max_file_size_mb),
            value_type="int",
            description="حداکثر اندازه فایل به مگابایت",
            updated_by_id=current_user.id
        )
    
    if settings_data.allowed_image_types is not None:
        set_setting(
            db,
            "allowed_image_types",
            ",".join(settings_data.allowed_image_types),
            value_type="string",
            description="انواع فایل تصویری مجاز",
            updated_by_id=current_user.id
        )
    
    if settings_data.allowed_document_types is not None:
        set_setting(
            db,
            "allowed_document_types",
            ",".join(settings_data.allowed_document_types),
            value_type="string",
            description="انواع فایل متنی مجاز",
            updated_by_id=current_user.id
        )
    
    # Return updated settings
    updated_settings = get_file_settings(db)
    return FileSettingsResponse(**updated_settings)


@router.get("", response_model=GeneralSettingsResponse)
async def get_settings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all general settings including telegram bot settings"""
    lang = resolve_lang(request, current_user)
    
    # Initialize defaults if needed
    initialize_default_settings(db)
    
    # Get all settings from database
    all_settings = get_all_settings(db)
    
    # Get bot started status from app state
    from app.main import app as fastapi_app
    telegram_bot_started = getattr(fastapi_app.state, "telegram_bot_started", False)
    
    # Map settings to response
    return GeneralSettingsResponse(
        telegram_bot_token=all_settings.get("telegram_bot_token"),
        telegram_bot_enabled=all_settings.get("telegram_bot_enabled", False),
        telegram_bot_started=telegram_bot_started,
        auto_start_bot=all_settings.get("auto_start_bot", False),
        send_ticket_notifications=all_settings.get("send_ticket_notifications", True),
        send_status_updates=all_settings.get("send_status_updates", True),
        send_sla_warnings=all_settings.get("send_sla_warnings", True),
        send_resolution_notifications=all_settings.get("send_resolution_notifications", True),
        notification_language=all_settings.get("notification_language", "auto"),
        welcome_message_enabled=all_settings.get("welcome_message_enabled", True),
        welcome_message_text=all_settings.get("welcome_message_text"),
        help_command_enabled=all_settings.get("help_command_enabled", True),
        help_command_text=all_settings.get("help_command_text"),
    )


@router.put("", response_model=GeneralSettingsResponse)
async def update_settings(
    request: Request,
    settings_data: GeneralSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_central_admin)
):
    """Update general settings (Central Admin only)"""
    lang = resolve_lang(request, current_user)
    
    # Update each setting if provided
    setting_mappings = {
        "telegram_bot_token": ("telegram_bot_token", "string", "توکن بات تلگرام"),
        "telegram_bot_enabled": ("telegram_bot_enabled", "bool", "فعال بودن بات تلگرام"),
        "auto_start_bot": ("auto_start_bot", "bool", "شروع خودکار بات"),
        "send_ticket_notifications": ("send_ticket_notifications", "bool", "ارسال اعلان تیکت"),
        "send_status_updates": ("send_status_updates", "bool", "ارسال به‌روزرسانی وضعیت"),
        "send_sla_warnings": ("send_sla_warnings", "bool", "ارسال هشدار SLA"),
        "send_resolution_notifications": ("send_resolution_notifications", "bool", "ارسال اعلان حل تیکت"),
        "notification_language": ("notification_language", "string", "زبان اعلان‌ها"),
        "welcome_message_enabled": ("welcome_message_enabled", "bool", "پیام خوش‌آمد فعال"),
        "welcome_message_text": ("welcome_message_text", "string", "متن پیام خوش‌آمد"),
        "help_command_enabled": ("help_command_enabled", "bool", "دستور help فعال"),
        "help_command_text": ("help_command_text", "string", "متن دستور help"),
    }
    
    for field_name, (setting_key, value_type, description) in setting_mappings.items():
        value = getattr(settings_data, field_name, None)
        if value is not None:
            if value_type == "bool":
                value_str = "true" if value else "false"
            else:
                value_str = str(value) if value else ""
            set_setting(
                db,
                setting_key,
                value_str,
                value_type=value_type,
                description=description,
                updated_by_id=current_user.id
            )
    
    # Get updated settings
    all_settings = get_all_settings(db)
    from app.main import app as fastapi_app
    telegram_bot_started = getattr(fastapi_app.state, "telegram_bot_started", False)
    
    return GeneralSettingsResponse(
        telegram_bot_token=all_settings.get("telegram_bot_token"),
        telegram_bot_enabled=all_settings.get("telegram_bot_enabled", False),
        telegram_bot_started=telegram_bot_started,
        auto_start_bot=all_settings.get("auto_start_bot", False),
        send_ticket_notifications=all_settings.get("send_ticket_notifications", True),
        send_status_updates=all_settings.get("send_status_updates", True),
        send_sla_warnings=all_settings.get("send_sla_warnings", True),
        send_resolution_notifications=all_settings.get("send_resolution_notifications", True),
        notification_language=all_settings.get("notification_language", "auto"),
        welcome_message_enabled=all_settings.get("welcome_message_enabled", True),
        welcome_message_text=all_settings.get("welcome_message_text"),
        help_command_enabled=all_settings.get("help_command_enabled", True),
        help_command_text=all_settings.get("help_command_text"),
    )

