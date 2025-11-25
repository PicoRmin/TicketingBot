"""
Service for managing Custom Fields
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models import CustomField, TicketCustomFieldValue, Ticket, Department, Branch
from app.models.custom_field import CustomFieldType
from app.schemas.custom_field import CustomFieldCreate, CustomFieldUpdate
from app.core.enums import TicketCategory
import logging

logger = logging.getLogger(__name__)


def get_custom_fields(
    db: Session,
    category: Optional[TicketCategory] = None,
    department_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[CustomField], int]:
    """
    Get all custom fields with filters
    
    Args:
        db: Database session
        category: Filter by ticket category
        department_id: Filter by department
        branch_id: Filter by branch
        is_active: Filter by active status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (custom fields list, total count)
    """
    query = db.query(CustomField).options(
        joinedload(CustomField.department),
        joinedload(CustomField.branch)
    )
    
    if category is not None:
        query = query.filter(
            or_(
                CustomField.category == category,
                CustomField.category.is_(None)  # Fields applicable to all categories
            )
        )
    
    if department_id is not None:
        query = query.filter(
            or_(
                CustomField.department_id == department_id,
                CustomField.department_id.is_(None)  # Fields applicable to all departments
            )
        )
    
    if branch_id is not None:
        query = query.filter(
            or_(
                CustomField.branch_id == branch_id,
                CustomField.branch_id.is_(None)  # Fields applicable to all branches
            )
        )
    
    if is_active is not None:
        query = query.filter(CustomField.is_active == is_active)
    
    total = query.count()
    custom_fields = query.order_by(
        CustomField.display_order.asc(),
        CustomField.name.asc()
    ).offset(skip).limit(limit).all()
    
    return custom_fields, total


def get_custom_field(db: Session, field_id: int) -> Optional[CustomField]:
    """Get a custom field by ID"""
    return (
        db.query(CustomField)
        .options(
            joinedload(CustomField.department),
            joinedload(CustomField.branch)
        )
        .filter(CustomField.id == field_id)
        .first()
    )


def get_custom_field_by_name(db: Session, name: str) -> Optional[CustomField]:
    """Get a custom field by name"""
    return db.query(CustomField).filter(CustomField.name == name).first()


def get_custom_fields_for_ticket(
    db: Session,
    ticket: Ticket
) -> List[CustomField]:
    """
    Get applicable custom fields for a ticket
    Based on ticket's category, department, and branch
    """
    query = db.query(CustomField).filter(CustomField.is_active == True)
    
    # Filter by category
    query = query.filter(
        or_(
            CustomField.category == ticket.category,
            CustomField.category.is_(None)
        )
    )
    
    # Filter by department
    if ticket.department_id:
        query = query.filter(
            or_(
                CustomField.department_id == ticket.department_id,
                CustomField.department_id.is_(None)
            )
        )
    
    # Filter by branch
    if ticket.branch_id:
        query = query.filter(
            or_(
                CustomField.branch_id == ticket.branch_id,
                CustomField.branch_id.is_(None)
            )
        )
    
    return query.order_by(
        CustomField.display_order.asc(),
        CustomField.name.asc()
    ).all()


def create_custom_field(db: Session, field_data: CustomFieldCreate) -> CustomField:
    """
    Create a new custom field
    
    Args:
        db: Database session
        field_data: Custom field data
        
    Returns:
        Created CustomField
    """
    # Check if field with same name exists
    existing = get_custom_field_by_name(db, field_data.name)
    if existing:
        raise ValueError(f"Custom field with name '{field_data.name}' already exists")
    
    # Validate department and branch if provided
    if field_data.department_id:
        dept = db.query(Department).filter(Department.id == field_data.department_id).first()
        if not dept:
            raise ValueError(f"Department with ID {field_data.department_id} not found")
    
    if field_data.branch_id:
        branch = db.query(Branch).filter(Branch.id == field_data.branch_id).first()
        if not branch:
            raise ValueError(f"Branch with ID {field_data.branch_id} not found")
    
    field_dict = field_data.dict()
    # Convert enum to string value for storage
    if 'field_type' in field_dict and hasattr(field_dict['field_type'], 'value'):
        field_dict['field_type'] = field_dict['field_type'].value
    custom_field = CustomField(**field_dict)
    db.add(custom_field)
    db.commit()
    db.refresh(custom_field)
    
    logger.info(f"Created custom field: {custom_field.name} (ID: {custom_field.id})")
    return custom_field


def update_custom_field(
    db: Session,
    custom_field: CustomField,
    field_data: CustomFieldUpdate
) -> CustomField:
    """
    Update a custom field
    
    Args:
        db: Database session
        custom_field: Custom field to update
        field_data: Update data
        
    Returns:
        Updated CustomField
    """
    update_data = field_data.dict(exclude_unset=True)
    
    # Validate department and branch if provided
    if 'department_id' in update_data and update_data['department_id']:
        dept = db.query(Department).filter(Department.id == update_data['department_id']).first()
        if not dept:
            raise ValueError(f"Department with ID {update_data['department_id']} not found")
    
    if 'branch_id' in update_data and update_data['branch_id']:
        branch = db.query(Branch).filter(Branch.id == update_data['branch_id']).first()
        if not branch:
            raise ValueError(f"Branch with ID {update_data['branch_id']} not found")
    
    for key, value in update_data.items():
        setattr(custom_field, key, value)
    
    db.commit()
    db.refresh(custom_field)
    
    logger.info(f"Updated custom field: {custom_field.name} (ID: {custom_field.id})")
    return custom_field


def delete_custom_field(db: Session, custom_field: CustomField) -> bool:
    """
    Delete a custom field
    
    Note: This will also delete all associated values
    
    Args:
        db: Database session
        custom_field: Custom field to delete
        
    Returns:
        True if deleted successfully
    """
    try:
        db.delete(custom_field)
        db.commit()
        logger.info(f"Deleted custom field: {custom_field.name} (ID: {custom_field.id})")
        return True
    except Exception as e:
        logger.error(f"Error deleting custom field: {e}", exc_info=True)
        db.rollback()
        return False


def get_ticket_custom_field_value(
    db: Session,
    ticket_id: int,
    custom_field_id: int
) -> Optional[TicketCustomFieldValue]:
    """Get custom field value for a ticket"""
    return (
        db.query(TicketCustomFieldValue)
        .filter(
            TicketCustomFieldValue.ticket_id == ticket_id,
            TicketCustomFieldValue.custom_field_id == custom_field_id
        )
        .first()
    )


def get_ticket_custom_field_values(
    db: Session,
    ticket_id: int
) -> List[TicketCustomFieldValue]:
    """Get all custom field values for a ticket"""
    return (
        db.query(TicketCustomFieldValue)
        .options(joinedload(TicketCustomFieldValue.custom_field))
        .filter(TicketCustomFieldValue.ticket_id == ticket_id)
        .all()
    )


def set_ticket_custom_field_value(
    db: Session,
    ticket_id: int,
    custom_field_id: int,
    value: Any
) -> TicketCustomFieldValue:
    """
    Set custom field value for a ticket
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        custom_field_id: Custom field ID
        value: Value to set (will be stored as JSON)
        
    Returns:
        Created or updated TicketCustomFieldValue
    """
    # Get or create value
    field_value = get_ticket_custom_field_value(db, ticket_id, custom_field_id)
    
    if field_value:
        field_value.value = value
        db.commit()
        db.refresh(field_value)
    else:
        field_value = TicketCustomFieldValue(
            ticket_id=ticket_id,
            custom_field_id=custom_field_id,
            value=value
        )
        db.add(field_value)
        db.commit()
        db.refresh(field_value)
    
    return field_value


def delete_ticket_custom_field_value(
    db: Session,
    ticket_id: int,
    custom_field_id: int
) -> bool:
    """Delete custom field value for a ticket"""
    field_value = get_ticket_custom_field_value(db, ticket_id, custom_field_id)
    if field_value:
        db.delete(field_value)
        db.commit()
        return True
    return False


def validate_custom_field_value(
    custom_field: CustomField,
    value: Any
) -> bool:
    """
    Validate a value against custom field configuration
    
    Args:
        custom_field: Custom field definition
        value: Value to validate
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    config = custom_field.config or {}
    
    # Required field validation
    if custom_field.is_required and (value is None or value == ""):
        raise ValueError(f"Field '{custom_field.label}' is required")
    
    # Type-specific validation
    if value is None or value == "":
        return True  # Empty values are allowed for non-required fields
    
    field_type_value = custom_field.field_type if isinstance(custom_field.field_type, str) else custom_field.field_type.value
    
    if field_type_value == CustomFieldType.NUMBER.value:
        try:
            num_value = float(value)
            if 'min' in config and num_value < config['min']:
                raise ValueError(f"Value must be at least {config['min']}")
            if 'max' in config and num_value > config['max']:
                raise ValueError(f"Value must be at most {config['max']}")
        except (ValueError, TypeError):
            raise ValueError(f"Value must be a number")
    
    elif field_type_value == CustomFieldType.SELECT.value:
        if 'options' in config:
            valid_values = [opt['value'] for opt in config['options']]
            if value not in valid_values:
                raise ValueError(f"Value must be one of: {', '.join(valid_values)}")
    
    elif field_type_value == CustomFieldType.MULTISELECT.value:
        if not isinstance(value, list):
            raise ValueError("Value must be a list for multiselect field")
        if 'options' in config:
            valid_values = [opt['value'] for opt in config['options']]
            for v in value:
                if v not in valid_values:
                    raise ValueError(f"All values must be from: {', '.join(valid_values)}")
    
    elif field_type_value in [CustomFieldType.TEXT.value, CustomFieldType.TEXTAREA.value]:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        if 'min_length' in config and len(value) < config['min_length']:
            raise ValueError(f"Value must be at least {config['min_length']} characters")
        if 'max_length' in config and len(value) > config['max_length']:
            raise ValueError(f"Value must be at most {config['max_length']} characters")
        if 'pattern' in config:
            import re
            if not re.match(config['pattern'], value):
                raise ValueError(f"Value does not match required pattern")
    
    elif field_type_value == CustomFieldType.EMAIL.value:
        if not isinstance(value, str) or '@' not in value:
            raise ValueError("Value must be a valid email address")
    
    elif field_type_value == CustomFieldType.URL.value:
        if not isinstance(value, str) or not (value.startswith('http://') or value.startswith('https://')):
            raise ValueError("Value must be a valid URL")
    
    elif field_type_value == CustomFieldType.BOOLEAN.value:
        if not isinstance(value, bool):
            raise ValueError("Value must be a boolean")
    
    return True

