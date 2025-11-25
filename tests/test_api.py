"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db, SessionLocal
from app.core.enums import UserRole, Language
from app.core.security import create_access_token
from app.models import User
from app.core.security import get_password_hash

# Override get_db dependency for testing
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_user_token():
    """Create a test user and return access token"""
    db = SessionLocal()
    try:
        user = User(
            username="apitest",
            full_name="API Test User",
            password_hash=get_password_hash("testpass"),
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


@pytest.fixture
def test_admin_token():
    """Create a test admin and return access token"""
    db = SessionLocal()
    try:
        admin = User(
            username="admintest",
            full_name="Admin Test",
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


def test_login_endpoint():
    """Test login endpoint"""
    db = SessionLocal()
    try:
        # First create a user
        from app.services.user_service import create_user
        from app.schemas.user import UserCreate
        
        user_data = UserCreate(
            username="logintest",
            full_name="Login Test",
            password="loginpass123",
            role=UserRole.USER,
            language=Language.FA
        )
        user = create_user(db, user_data)
        
        # Test login
        response = client.post(
            "/api/auth/login",
            data={"username": "logintest", "password": "loginpass123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        
        # Cleanup
        db.delete(user)
        db.commit()
    finally:
        db.close()


def test_get_tickets_endpoint(test_user_token):
    """Test getting tickets endpoint"""
    token, user = test_user_token
    
    response = client.get(
        "/api/tickets",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_create_ticket_endpoint(test_user_token):
    """Test creating a ticket"""
    token, user = test_user_token
    
    ticket_data = {
        "title": "تیکت تست API",
        "description": "توضیحات تست",
        "category": "software",
        "priority": "medium"
    }
    
    response = client.post(
        "/api/tickets",
        json=ticket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "تیکت تست API"
    assert data["ticket_number"].startswith("T-")


def test_get_ticket_by_id_endpoint(test_user_token):
    """Test getting a ticket by ID"""
    token, user = test_user_token
    db = SessionLocal()
    try:
        # First create a ticket
        from app.services.ticket_service import create_ticket
        from app.schemas.ticket import TicketCreate
        from app.core.enums import TicketCategory, TicketPriority
        
        ticket_data = TicketCreate(
            title="تیکت تست",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket = create_ticket(db, ticket_data, user.id)
        
        # Test getting the ticket
        response = client.get(
            f"/api/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket.id
        assert data["ticket_number"] == ticket.ticket_number
        
        # Cleanup
        db.delete(ticket)
        db.commit()
    finally:
        db.close()


def test_unauthorized_access():
    """Test that unauthorized requests are rejected"""
    response = client.get("/api/tickets")
    
    assert response.status_code == 401


def test_invalid_token():
    """Test that invalid tokens are rejected"""
    response = client.get(
        "/api/tickets",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


