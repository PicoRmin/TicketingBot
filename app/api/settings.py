"""
Settings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.settings import FileSettingsResponse, FileSettingsUpdate, SettingsResponse
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

