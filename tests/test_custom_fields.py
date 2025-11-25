"""
Unit tests for Custom Fields
"""
import pytest
from app.models import CustomField, TicketCustomFieldValue, Ticket, Department, Branch
from app.models.custom_field import CustomFieldType
from app.services.custom_field_service import (
    create_custom_field,
    get_custom_field,
    get_custom_fields,
    update_custom_field,
    delete_custom_field,
    get_custom_fields_for_ticket,
    set_ticket_custom_field_value,
    get_ticket_custom_field_values,
    validate_custom_field_value
)
from app.schemas.custom_field import CustomFieldCreate, CustomFieldUpdate
from app.core.enums import TicketCategory, TicketStatus, TicketPriority


def test_create_custom_field(db):
    """Test creating a custom field"""
    field_data = CustomFieldCreate(
        name="test_field",
        label="فیلد تست",
        label_en="Test Field",
        field_type=CustomFieldType.TEXT,
        description="این یک فیلد تست است",
        is_required=False,
        is_active=True
    )
    
    custom_field = create_custom_field(db, field_data)
    
    assert custom_field.id is not None
    assert custom_field.name == "test_field"
    assert custom_field.label == "فیلد تست"
    assert custom_field.field_type == CustomFieldType.TEXT.value
    assert custom_field.is_active is True


def test_create_custom_field_with_select_options(db):
    """Test creating a custom field with SELECT type and options"""
    field_data = CustomFieldCreate(
        name="priority_level",
        label="سطح اولویت",
        field_type=CustomFieldType.SELECT,
        config={
            "options": [
                {"value": "low", "label": "پایین"},
                {"value": "medium", "label": "متوسط"},
                {"value": "high", "label": "بالا"}
            ]
        },
        is_required=True
    )
    
    custom_field = create_custom_field(db, field_data)
    
    assert custom_field.field_type == CustomFieldType.SELECT.value
    assert custom_field.config is not None
    assert "options" in custom_field.config
    assert len(custom_field.config["options"]) == 3


def test_get_custom_field(db):
    """Test getting a custom field"""
    field_data = CustomFieldCreate(
        name="get_test",
        label="تست دریافت",
        field_type=CustomFieldType.TEXT
    )
    created = create_custom_field(db, field_data)
    
    retrieved = get_custom_field(db, created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "get_test"


def test_get_custom_fields_with_filters(db, test_department):
    """Test getting custom fields with filters"""
    # Create fields for different categories
    field1 = create_custom_field(db, CustomFieldCreate(
        name="field1",
        label="فیلد 1",
        field_type=CustomFieldType.TEXT,
        category=TicketCategory.SOFTWARE
    ))
    
    field2 = create_custom_field(db, CustomFieldCreate(
        name="field2",
        label="فیلد 2",
        field_type=CustomFieldType.NUMBER,
        category=TicketCategory.INTERNET
    ))
    
    field3 = create_custom_field(db, CustomFieldCreate(
        name="field3",
        label="فیلد 3",
        field_type=CustomFieldType.BOOLEAN,
        department_id=test_department.id
    ))
    
    # Test filter by category
    fields, total = get_custom_fields(db, category=TicketCategory.SOFTWARE)
    assert total >= 1
    assert any(f.id == field1.id for f in fields)
    
    # Test filter by department
    fields, total = get_custom_fields(db, department_id=test_department.id)
    assert total >= 1
    assert any(f.id == field3.id for f in fields)


def test_update_custom_field(db):
    """Test updating a custom field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="update_test",
        label="تست به‌روزرسانی",
        field_type=CustomFieldType.TEXT,
        is_required=False
    ))
    
    update_data = CustomFieldUpdate(
        label="برچسب جدید",
        is_required=True,
        help_text="متن راهنما"
    )
    
    updated = update_custom_field(db, field, update_data)
    
    assert updated.label == "برچسب جدید"
    assert updated.is_required is True
    assert updated.help_text == "متن راهنما"


def test_delete_custom_field(db):
    """Test deleting a custom field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="delete_test",
        label="تست حذف",
        field_type=CustomFieldType.TEXT
    ))
    
    success = delete_custom_field(db, field)
    
    assert success is True
    
    # Verify deletion
    deleted = get_custom_field(db, field.id)
    assert deleted is None


def test_get_custom_fields_for_ticket(db, test_ticket, test_department):
    """Test getting applicable custom fields for a ticket"""
    # Create field for ticket's category
    field1 = create_custom_field(db, CustomFieldCreate(
        name="category_field",
        label="فیلد دسته‌بندی",
        field_type=CustomFieldType.TEXT,
        category=test_ticket.category
    ))
    
    # Create field for different category (should not appear)
    field2 = create_custom_field(db, CustomFieldCreate(
        name="other_category",
        label="دسته‌بندی دیگر",
        field_type=CustomFieldType.TEXT,
        category=TicketCategory.INTERNET
    ))
    
    # Create field for department
    test_ticket.department_id = test_department.id
    db.commit()
    
    field3 = create_custom_field(db, CustomFieldCreate(
        name="dept_field",
        label="فیلد دپارتمان",
        field_type=CustomFieldType.NUMBER,
        department_id=test_department.id
    ))
    
    applicable_fields = get_custom_fields_for_ticket(db, test_ticket)
    
    # Should include field1 and field3, but not field2
    field_ids = [f.id for f in applicable_fields]
    assert field1.id in field_ids
    assert field3.id in field_ids
    assert field2.id not in field_ids


def test_set_ticket_custom_field_value(db, test_ticket):
    """Test setting custom field value for a ticket"""
    field = create_custom_field(db, CustomFieldCreate(
        name="value_test",
        label="تست مقدار",
        field_type=CustomFieldType.TEXT
    ))
    
    value = set_ticket_custom_field_value(db, test_ticket.id, field.id, "مقدار تست")
    
    assert value.id is not None
    assert value.ticket_id == test_ticket.id
    assert value.custom_field_id == field.id
    assert value.value == "مقدار تست"


def test_update_ticket_custom_field_value(db, test_ticket):
    """Test updating existing custom field value"""
    field = create_custom_field(db, CustomFieldCreate(
        name="update_value",
        label="به‌روزرسانی مقدار",
        field_type=CustomFieldType.TEXT
    ))
    
    # Set initial value
    value1 = set_ticket_custom_field_value(db, test_ticket.id, field.id, "مقدار اول")
    
    # Update value
    value2 = set_ticket_custom_field_value(db, test_ticket.id, field.id, "مقدار جدید")
    
    assert value1.id == value2.id  # Same record
    assert value2.value == "مقدار جدید"


def test_get_ticket_custom_field_values(db, test_ticket):
    """Test getting all custom field values for a ticket"""
    field1 = create_custom_field(db, CustomFieldCreate(
        name="field1",
        label="فیلد 1",
        field_type=CustomFieldType.TEXT
    ))
    
    field2 = create_custom_field(db, CustomFieldCreate(
        name="field2",
        label="فیلد 2",
        field_type=CustomFieldType.NUMBER
    ))
    
    set_ticket_custom_field_value(db, test_ticket.id, field1.id, "مقدار 1")
    set_ticket_custom_field_value(db, test_ticket.id, field2.id, 42)
    
    values = get_ticket_custom_field_values(db, test_ticket.id)
    
    assert len(values) == 2
    value_dict = {v.custom_field_id: v.value for v in values}
    assert value_dict[field1.id] == "مقدار 1"
    assert value_dict[field2.id] == 42


def test_validate_custom_field_value_text(db):
    """Test validating text field value"""
    field = create_custom_field(db, CustomFieldCreate(
        name="text_field",
        label="فیلد متن",
        field_type=CustomFieldType.TEXT,
        config={"min_length": 3, "max_length": 10}
    ))
    
    # Valid value
    assert validate_custom_field_value(field, "test") is True
    
    # Too short
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "ab")
    
    # Too long
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "this is too long")


def test_validate_custom_field_value_number(db):
    """Test validating number field value"""
    field = create_custom_field(db, CustomFieldCreate(
        name="number_field",
        label="فیلد عدد",
        field_type=CustomFieldType.NUMBER,
        config={"min": 0, "max": 100}
    ))
    
    # Valid value
    assert validate_custom_field_value(field, 50) is True
    
    # Too small
    with pytest.raises(ValueError):
        validate_custom_field_value(field, -1)
    
    # Too large
    with pytest.raises(ValueError):
        validate_custom_field_value(field, 101)


def test_validate_custom_field_value_select(db):
    """Test validating select field value"""
    field = create_custom_field(db, CustomFieldCreate(
        name="select_field",
        label="فیلد انتخاب",
        field_type=CustomFieldType.SELECT,
        config={
            "options": [
                {"value": "opt1", "label": "گزینه 1"},
                {"value": "opt2", "label": "گزینه 2"}
            ]
        }
    ))
    
    # Valid value
    assert validate_custom_field_value(field, "opt1") is True
    
    # Invalid value
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "invalid_option")


def test_validate_custom_field_value_multiselect(db):
    """Test validating multiselect field value"""
    field = create_custom_field(db, CustomFieldCreate(
        name="multiselect_field",
        label="فیلد چند انتخابی",
        field_type=CustomFieldType.MULTISELECT,
        config={
            "options": [
                {"value": "opt1", "label": "گزینه 1"},
                {"value": "opt2", "label": "گزینه 2"},
                {"value": "opt3", "label": "گزینه 3"}
            ]
        }
    ))
    
    # Valid values
    assert validate_custom_field_value(field, ["opt1", "opt2"]) is True
    
    # Invalid value in list
    with pytest.raises(ValueError):
        validate_custom_field_value(field, ["opt1", "invalid"])


def test_validate_custom_field_value_required(db):
    """Test validating required field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="required_field",
        label="فیلد اجباری",
        field_type=CustomFieldType.TEXT,
        is_required=True
    ))
    
    # Empty value should fail
    with pytest.raises(ValueError):
        validate_custom_field_value(field, None)
    
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "")
    
    # Valid value
    assert validate_custom_field_value(field, "test") is True


def test_validate_custom_field_value_email(db):
    """Test validating email field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="email_field",
        label="ایمیل",
        field_type=CustomFieldType.EMAIL
    ))
    
    # Valid email
    assert validate_custom_field_value(field, "test@example.com") is True
    
    # Invalid email
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "not-an-email")


def test_validate_custom_field_value_url(db):
    """Test validating URL field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="url_field",
        label="آدرس وب",
        field_type=CustomFieldType.URL
    ))
    
    # Valid URL
    assert validate_custom_field_value(field, "https://example.com") is True
    assert validate_custom_field_value(field, "http://example.com") is True
    
    # Invalid URL
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "not-a-url")


def test_validate_custom_field_value_boolean(db):
    """Test validating boolean field"""
    field = create_custom_field(db, CustomFieldCreate(
        name="boolean_field",
        label="بولی",
        field_type=CustomFieldType.BOOLEAN
    ))
    
    # Valid boolean
    assert validate_custom_field_value(field, True) is True
    assert validate_custom_field_value(field, False) is True
    
    # Invalid value
    with pytest.raises(ValueError):
        validate_custom_field_value(field, "not-boolean")

