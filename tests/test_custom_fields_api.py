"""
Integration tests for Custom Fields API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, CustomField, Ticket
from app.core.enums import UserRole, Language, TicketCategory, TicketStatus, TicketPriority
from app.core.security import get_password_hash, create_access_token
from app.models.custom_field import CustomFieldType

client = TestClient(app)


@pytest.fixture
def test_admin_token():
    """Create a test admin and return access token"""
    db = SessionLocal()
    try:
        admin = User(
            username="admin_custom",
            full_name="Admin Custom",
            password_hash=get_password_hash("adminpass"),
            role=UserRole.ADMIN,
            language=Language.FA,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        token = create_access_token(data={"sub": admin.username, "user_id": admin.id})
        yield token, admin
        
        db.delete(admin)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def test_user_token():
    """Create a test user and return access token"""
    db = SessionLocal()
    try:
        user = User(
            username="user_custom",
            full_name="User Custom",
            password_hash=get_password_hash("userpass"),
            role=UserRole.USER,
            language=Language.FA,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        token = create_access_token(data={"sub": user.username, "user_id": user.id})
        yield token, user
        
        db.delete(user)
        db.commit()
    finally:
        db.close()


def test_create_custom_field_api(test_admin_token):
    """Test creating a custom field via API"""
    token, admin = test_admin_token
    
    import time
    unique_name = f"api_test_field_{int(time.time())}"
    
    field_data = {
        "name": unique_name,
        "label": "فیلد تست API",
        "label_en": "API Test Field",
        "field_type": "text",
        "description": "این یک فیلد تست است",
        "is_required": False,
        "is_active": True
    }
    
    response = client.post(
        "/api/custom-fields",
        json=field_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 201:
        print(f"Response: {response.status_code}")
        print(f"Body: {response.json()}")
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == unique_name
    assert data["label"] == "فیلد تست API"
    assert data["field_type"] == "text"


def test_get_custom_fields_api(test_admin_token):
    """Test getting list of custom fields via API"""
    token, admin = test_admin_token
    
    # Create a field first
    db = SessionLocal()
    try:
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="list_test",
            label="تست لیست",
            field_type=CustomFieldType.TEXT
        ))
        
        # Get list
        response = client.get(
            "/api/custom-fields",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Cleanup
        db.delete(field)
        db.commit()
    finally:
        db.close()


def test_get_custom_field_by_id_api(test_admin_token):
    """Test getting a custom field by ID via API"""
    token, admin = test_admin_token
    
    db = SessionLocal()
    try:
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="get_by_id_test",
            label="تست دریافت با ID",
            field_type=CustomFieldType.TEXT
        ))
        
        response = client.get(
            f"/api/custom-fields/{field.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == field.id
        assert data["name"] == "get_by_id_test"
        
        # Cleanup
        db.delete(field)
        db.commit()
    finally:
        db.close()


def test_update_custom_field_api(test_admin_token):
    """Test updating a custom field via API"""
    token, admin = test_admin_token
    
    db = SessionLocal()
    try:
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="update_api_test",
            label="تست به‌روزرسانی API",
            field_type=CustomFieldType.TEXT
        ))
        
        update_data = {
            "label": "برچسب جدید",
            "is_required": True
        }
        
        response = client.patch(
            f"/api/custom-fields/{field.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "برچسب جدید"
        assert data["is_required"] is True
        
        # Cleanup
        db.delete(field)
        db.commit()
    finally:
        db.close()


def test_delete_custom_field_api(test_admin_token):
    """Test deleting a custom field via API"""
    token, admin = test_admin_token
    
    db = SessionLocal()
    try:
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="delete_api_test",
            label="تست حذف API",
            field_type=CustomFieldType.TEXT
        ))
        field_id = field.id
        
        response = client.delete(
            f"/api/custom-fields/{field_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(
            f"/api/custom-fields/{field_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
    finally:
        db.close()


def test_get_ticket_custom_fields_api(test_user_token):
    """Test getting custom fields for a ticket via API"""
    token, user = test_user_token
    
    db = SessionLocal()
    try:
        # Create a ticket
        from app.services.ticket_service import create_ticket
        from app.schemas.ticket import TicketCreate
        
        ticket = create_ticket(db, TicketCreate(
            title="تیکت تست",
            description="این یک تیکت تستی است برای بررسی فیلدهای سفارشی",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        ), user.id)
        
        # Create a custom field for this category
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="ticket_field_test",
            label="فیلد تیکت",
            field_type=CustomFieldType.TEXT,
            category=TicketCategory.SOFTWARE
        ))
        
        # Get custom fields for ticket
        response = client.get(
            f"/api/custom-fields/ticket/{ticket.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(f["id"] == field.id for f in data)
        
        # Cleanup
        db.delete(field)
        db.delete(ticket)
        db.commit()
    finally:
        db.close()


def test_set_ticket_custom_field_values_api(test_user_token):
    """Test setting custom field values for a ticket via API"""
    token, user = test_user_token
    
    db = SessionLocal()
    try:
        # Create a ticket
        from app.services.ticket_service import create_ticket
        from app.schemas.ticket import TicketCreate
        
        ticket = create_ticket(db, TicketCreate(
            title="تیکت تست",
            description="این یک تیکت تستی است برای بررسی فیلدهای سفارشی",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        ), user.id)
        
        # Create a custom field
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name="value_test_field",
            label="فیلد مقدار",
            field_type=CustomFieldType.TEXT,
            category=TicketCategory.SOFTWARE
        ))
        
        # Set value
        values_data = {
            "values": [
                {
                    "custom_field_id": field.id,
                    "value": "مقدار تست"
                }
            ]
        }
        
        response = client.post(
            f"/api/custom-fields/ticket/{ticket.id}/values",
            json=values_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["value"] == "مقدار تست"
        
        # Cleanup
        db.delete(field)
        db.delete(ticket)
        db.commit()
    finally:
        db.close()


def test_unauthorized_access_custom_fields(test_user_token):
    """Test that regular users cannot access admin endpoints"""
    token, user = test_user_token
    
    # Regular user should not be able to create custom fields
    response = client.post(
        "/api/custom-fields",
        json={
            "name": "unauthorized",
            "label": "غیرمجاز",
            "field_type": "text"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403


def test_custom_field_validation_api(test_admin_token):
    """Test custom field validation via API"""
    token, admin = test_admin_token
    
    db = SessionLocal()
    try:
        import time
        unique_name = f"select_validation_{int(time.time())}"
        
        # Clean up any existing field with similar name
        from app.services.custom_field_service import get_custom_field_by_name
        existing = get_custom_field_by_name(db, "select_validation")
        if existing:
            db.delete(existing)
            db.commit()
        
        # Create a field with SELECT type
        from app.services.custom_field_service import create_custom_field
        from app.schemas.custom_field import CustomFieldCreate
        
        field = create_custom_field(db, CustomFieldCreate(
            name=unique_name,
            label="انتخاب",
            field_type=CustomFieldType.SELECT,
            config={
                "options": [
                    {"value": "opt1", "label": "گزینه 1"},
                    {"value": "opt2", "label": "گزینه 2"}
                ]
            },
            is_required=True
        ))
        
        # Create a ticket
        from app.services.ticket_service import create_ticket
        from app.schemas.ticket import TicketCreate
        
        ticket = create_ticket(db, TicketCreate(
            title="تیکت تست",
            description="این یک تیکت تستی است برای بررسی فیلدهای سفارشی",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        ), admin.id)
        
        # Try to set invalid value
        values_data = {
            "values": [
                {
                    "custom_field_id": field.id,
                    "value": "invalid_option"
                }
            ]
        }
        
        response = client.post(
            f"/api/custom-fields/ticket/{ticket.id}/values",
            json=values_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Value must be one of" in response.json()["detail"]
        
        # Cleanup
        db.delete(field)
        db.delete(ticket)
        db.commit()
    finally:
        db.close()

