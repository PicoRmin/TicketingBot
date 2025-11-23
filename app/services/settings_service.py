"""
Settings service for managing system settings
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import SystemSettings

# Default allowed file types (defined here to avoid circular import)
_DEFAULT_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_DEFAULT_ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

# Default settings
DEFAULT_SETTINGS = {
    "max_images_per_ticket": 10,
    "max_documents_per_ticket": 5,
    "max_file_size_mb": 10,
    "allowed_image_types": ",".join(sorted(_DEFAULT_ALLOWED_IMAGE_TYPES)),
    "allowed_document_types": ",".join(sorted(_DEFAULT_ALLOWED_DOCUMENT_TYPES)),
}


def get_setting(db: Session, key: str, default: Optional[Any] = None) -> Optional[str]:
    """Get a setting value by key"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if setting:
        return setting.value
    # Return default if exists
    if key in DEFAULT_SETTINGS:
        return str(DEFAULT_SETTINGS[key])
    return default


def set_setting(
    db: Session,
    key: str,
    value: str,
    value_type: str = "string",
    description: Optional[str] = None,
    updated_by_id: Optional[int] = None
) -> SystemSettings:
    """Set or update a setting"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if setting:
        setting.value = value
        setting.value_type = value_type
        if description:
            setting.description = description
        if updated_by_id:
            setting.updated_by_id = updated_by_id
    else:
        setting = SystemSettings(
            key=key,
            value=value,
            value_type=value_type,
            description=description,
            updated_by_id=updated_by_id
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting


def get_all_settings(db: Session) -> Dict[str, Any]:
    """Get all settings as a dictionary"""
    settings = db.query(SystemSettings).all()
    result = {}
    
    # Add defaults first
    for key, value in DEFAULT_SETTINGS.items():
        result[key] = value
    
    # Override with database values
    for setting in settings:
        if setting.value_type == "int":
            try:
                result[setting.key] = int(setting.value)
            except (ValueError, TypeError):
                result[setting.key] = setting.value
        elif setting.value_type == "bool":
            result[setting.key] = setting.value.lower() in ("true", "1", "yes")
        elif setting.value_type == "json":
            import json
            try:
                result[setting.key] = json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                result[setting.key] = setting.value
        else:
            result[setting.key] = setting.value
    
    return result


def get_file_settings(db: Session) -> Dict[str, Any]:
    """Get file-related settings"""
    all_settings = get_all_settings(db)
    return {
        "max_images_per_ticket": int(all_settings.get("max_images_per_ticket", DEFAULT_SETTINGS["max_images_per_ticket"])),
        "max_documents_per_ticket": int(all_settings.get("max_documents_per_ticket", DEFAULT_SETTINGS["max_documents_per_ticket"])),
        "max_file_size_mb": int(all_settings.get("max_file_size_mb", DEFAULT_SETTINGS["max_file_size_mb"])),
        "allowed_image_types": all_settings.get("allowed_image_types", DEFAULT_SETTINGS["allowed_image_types"]).split(",") if isinstance(all_settings.get("allowed_image_types"), str) else all_settings.get("allowed_image_types", []),
        "allowed_document_types": all_settings.get("allowed_document_types", DEFAULT_SETTINGS["allowed_document_types"]).split(",") if isinstance(all_settings.get("allowed_document_types"), str) else all_settings.get("allowed_document_types", []),
    }


def initialize_default_settings(db: Session) -> None:
    """Initialize default settings if they don't exist"""
    for key, value in DEFAULT_SETTINGS.items():
        existing = db.query(SystemSettings).filter(SystemSettings.key == key).first()
        if not existing:
            set_setting(db, key, str(value), value_type="int" if isinstance(value, int) else "string")

