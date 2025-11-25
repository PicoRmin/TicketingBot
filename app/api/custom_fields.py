"""
API endpoints for Custom Fields management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.deps import get_current_active_user, require_admin
from app.models import User, CustomField, Ticket
from app.schemas.custom_field import (
    CustomFieldCreate,
    CustomFieldUpdate,
    CustomFieldResponse,
    TicketCustomFieldValueCreate,
    TicketCustomFieldValueResponse,
    CustomFieldWithValue,
    BulkCustomFieldValuesUpdate
)
from app.services.custom_field_service import (
    get_custom_fields,
    get_custom_field,
    create_custom_field,
    update_custom_field,
    delete_custom_field,
    get_custom_fields_for_ticket,
    get_ticket_custom_field_values,
    set_ticket_custom_field_value,
    delete_ticket_custom_field_value,
    validate_custom_field_value
)
from app.core.enums import TicketCategory

router = APIRouter()


@router.get("", response_model=List[CustomFieldResponse])
async def list_custom_fields(
    category: Optional[TicketCategory] = Query(None, description="Filter by ticket category"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get list of custom fields"""
    custom_fields, total = get_custom_fields(
        db,
        category=category,
        department_id=department_id,
        branch_id=branch_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return custom_fields


@router.get("/{field_id}", response_model=CustomFieldResponse)
async def get_custom_field_by_id(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get a custom field by ID"""
    custom_field = get_custom_field(db, field_id)
    if not custom_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field not found"
        )
    return custom_field


@router.post("", response_model=CustomFieldResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_field_endpoint(
    field_data: CustomFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new custom field"""
    try:
        custom_field = create_custom_field(db, field_data)
        return custom_field
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{field_id}", response_model=CustomFieldResponse)
async def update_custom_field_endpoint(
    field_id: int,
    field_data: CustomFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a custom field"""
    custom_field = get_custom_field(db, field_id)
    if not custom_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field not found"
        )
    
    try:
        updated = update_custom_field(db, custom_field, field_data)
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_field_endpoint(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a custom field"""
    custom_field = get_custom_field(db, field_id)
    if not custom_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field not found"
        )
    
    success = delete_custom_field(db, custom_field)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete custom field"
        )


@router.get("/ticket/{ticket_id}", response_model=List[CustomFieldWithValue])
async def get_ticket_custom_fields(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get custom fields applicable to a ticket with their values"""
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check access
    if current_user.role.value == "user" and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ticket"
        )
    
    # Get applicable custom fields
    custom_fields = get_custom_fields_for_ticket(db, ticket)
    
    # Get existing values
    values = get_ticket_custom_field_values(db, ticket_id)
    values_dict = {v.custom_field_id: v for v in values}
    
    # Combine fields with values
    result = []
    for field in custom_fields:
        field_dict = {
            "id": field.id,
            "name": field.name,
            "label": field.label,
            "label_en": field.label_en,
            "field_type": field.field_type,
            "description": field.description,
            "config": field.config,
            "category": field.category,
            "department_id": field.department_id,
            "branch_id": field.branch_id,
            "is_required": field.is_required,
            "is_visible_to_user": field.is_visible_to_user,
            "is_editable_by_user": field.is_editable_by_user,
            "default_value": field.default_value,
            "display_order": field.display_order,
            "help_text": field.help_text,
            "placeholder": field.placeholder,
            "is_active": field.is_active,
            "created_at": field.created_at,
            "updated_at": field.updated_at,
            "value": None,
            "value_id": None
        }
        
        if field.id in values_dict:
            field_dict["value"] = values_dict[field.id].value
            field_dict["value_id"] = values_dict[field.id].id
        elif field.default_value:
            field_dict["value"] = field.default_value
        
        result.append(CustomFieldWithValue(**field_dict))
    
    return result


@router.post("/ticket/{ticket_id}/values", response_model=List[TicketCustomFieldValueResponse])
async def set_ticket_custom_field_values(
    ticket_id: int,
    values_data: BulkCustomFieldValuesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Set custom field values for a ticket"""
    # Get ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check access
    if current_user.role.value == "user" and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this ticket"
        )
    
    # Validate and set values
    result = []
    for value_data in values_data.values:
        # Get custom field
        custom_field = get_custom_field(db, value_data.custom_field_id)
        if not custom_field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Custom field with ID {value_data.custom_field_id} not found"
            )
        
        # Check if field is applicable to this ticket
        applicable_fields = get_custom_fields_for_ticket(db, ticket)
        if custom_field not in applicable_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Custom field '{custom_field.name}' is not applicable to this ticket"
            )
        
        # Check edit permission for users
        if current_user.role.value == "user" and not custom_field.is_editable_by_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Custom field '{custom_field.label}' is not editable by users"
            )
        
        # Validate value
        try:
            validate_custom_field_value(custom_field, value_data.value)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Set value
        field_value = set_ticket_custom_field_value(
            db,
            ticket_id,
            value_data.custom_field_id,
            value_data.value
        )
        result.append(field_value)
    
    return result


@router.delete("/ticket/{ticket_id}/values/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_custom_field_value_endpoint(
    ticket_id: int,
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a custom field value for a ticket"""
    success = delete_ticket_custom_field_value(db, ticket_id, field_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field value not found"
        )

