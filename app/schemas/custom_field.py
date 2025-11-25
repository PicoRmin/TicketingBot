"""
Schemas for Custom Fields
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from app.models.custom_field import CustomFieldType
from app.core.enums import TicketCategory


class CustomFieldConfig(BaseModel):
    """Configuration for custom field"""
    # For SELECT/MULTISELECT
    options: Optional[List[Dict[str, str]]] = None  # [{"value": "opt1", "label": "Option 1"}]
    
    # For NUMBER
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    
    # For TEXT/TEXTAREA
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # Regex pattern
    
    # For DATE/DATETIME
    min_date: Optional[str] = None  # ISO format
    max_date: Optional[str] = None  # ISO format
    
    class Config:
        extra = "allow"  # Allow additional fields for future extensibility


class CustomFieldBase(BaseModel):
    """Base schema for Custom Field"""
    name: str = Field(..., min_length=1, max_length=255, description="Field name (internal)")
    label: str = Field(..., min_length=1, max_length=255, description="Display label")
    label_en: Optional[str] = Field(None, max_length=255, description="English display label")
    field_type: CustomFieldType = Field(..., description="Field type")
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    # Visibility and scope
    category: Optional[TicketCategory] = None
    department_id: Optional[int] = None
    branch_id: Optional[int] = None
    
    # Field properties
    is_required: bool = False
    is_visible_to_user: bool = True
    is_editable_by_user: bool = True
    default_value: Optional[str] = None
    
    # Display settings
    display_order: int = 0
    help_text: Optional[str] = None
    placeholder: Optional[str] = Field(None, max_length=255)
    
    # Status
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        """Validate field name (must be valid identifier)"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Field name must contain only alphanumeric characters, underscores, and hyphens")
        return v.lower().replace(' ', '_')
    
    @validator('config')
    def validate_config(cls, v, values):
        """Validate configuration based on field type"""
        if not v:
            return v
        
        field_type = values.get('field_type')
        if not field_type:
            return v
        
        # Validate SELECT/MULTISELECT options
        if field_type in [CustomFieldType.SELECT, CustomFieldType.MULTISELECT]:
            if 'options' not in v or not isinstance(v['options'], list):
                raise ValueError("SELECT/MULTISELECT fields must have 'options' array in config")
            for opt in v['options']:
                if not isinstance(opt, dict) or 'value' not in opt or 'label' not in opt:
                    raise ValueError("Each option must have 'value' and 'label' keys")
        
        # Validate NUMBER constraints
        if field_type == CustomFieldType.NUMBER:
            if 'min' in v and 'max' in v:
                if v['min'] > v['max']:
                    raise ValueError("min must be less than or equal to max")
        
        return v


class CustomFieldCreate(CustomFieldBase):
    """Schema for creating a custom field"""
    pass


class CustomFieldUpdate(BaseModel):
    """Schema for updating a custom field"""
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    label_en: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    category: Optional[TicketCategory] = None
    department_id: Optional[int] = None
    branch_id: Optional[int] = None
    is_required: Optional[bool] = None
    is_visible_to_user: Optional[bool] = None
    is_editable_by_user: Optional[bool] = None
    default_value: Optional[str] = None
    display_order: Optional[int] = None
    help_text: Optional[str] = None
    placeholder: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class CustomFieldResponse(CustomFieldBase):
    """Schema for custom field response"""
    id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[Dict[str, Any]] = None
    branch: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class TicketCustomFieldValueBase(BaseModel):
    """Base schema for ticket custom field value"""
    custom_field_id: int
    value: Optional[Union[str, int, float, bool, List[str], Dict[str, Any]]] = None


class TicketCustomFieldValueCreate(TicketCustomFieldValueBase):
    """Schema for creating ticket custom field value"""
    pass


class TicketCustomFieldValueUpdate(BaseModel):
    """Schema for updating ticket custom field value"""
    value: Optional[Union[str, int, float, bool, List[str], Dict[str, Any]]] = None


class TicketCustomFieldValueResponse(TicketCustomFieldValueBase):
    """Schema for ticket custom field value response"""
    id: int
    ticket_id: int
    created_at: datetime
    updated_at: datetime
    custom_field: Optional[CustomFieldResponse] = None
    
    class Config:
        from_attributes = True


class CustomFieldWithValue(CustomFieldResponse):
    """Custom field with its value for a ticket"""
    value: Optional[Union[str, int, float, bool, List[str], Dict[str, Any]]] = None
    value_id: Optional[int] = None  # ID of TicketCustomFieldValue if exists


class BulkCustomFieldValuesUpdate(BaseModel):
    """Schema for bulk updating custom field values for a ticket"""
    values: List[TicketCustomFieldValueCreate] = Field(..., description="List of custom field values")

