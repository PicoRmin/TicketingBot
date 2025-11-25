"""
تست‌های یکپارچه‌سازی برای API Endpoints
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db, SessionLocal
from app.core.enums import UserRole, Language, TicketCategory, TicketStatus, TicketPriority
from app.core.security import create_access_token, get_password_hash
from app.models import User, Ticket, Branch, Department, Comment, SLARule
from app.services import ticket_service, user_service, branch_service, department_service
from app.schemas.ticket import TicketCreate
from app.schemas.user import UserCreate
from app.schemas.branch import BranchCreate
from app.schemas.department import DepartmentCreate
import tempfile
import os
import asyncio
from app.services import comment_service
import asyncio

# Override get_db dependency for testing
def override_get_db():
    """Override get_db for testing"""
    # Create test database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_with_token(test_db):
    """Create a test user and return access token"""
    user_data = UserCreate(
        username="apitest",
        full_name="API Test User",
        password="testpass123",
        role=UserRole.USER,
        language=Language.FA
    )
    user = user_service.create_user(test_db, user_data)
    
    token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role.value})
    return token, user


@pytest.fixture
def test_admin_with_token(test_db):
    """Create a test admin and return access token"""
    user_data = UserCreate(
        username="admintest",
        full_name="Admin Test",
        password="adminpass123",
        role=UserRole.ADMIN,
        language=Language.FA
    )
    admin = user_service.create_user(test_db, user_data)
    
    token = create_access_token(data={"sub": admin.username, "user_id": admin.id, "role": admin.role.value})
    return token, admin


@pytest.fixture
def test_branch_data(test_db):
    """Create a test branch"""
    branch_data = BranchCreate(
        name="شعبه تست",
        name_en="Test Branch",
        code="TEST",
        is_active=True
    )
    branch = branch_service.create_branch(test_db, branch_data)
    return branch


@pytest.fixture
def test_department_data(test_db):
    """Create a test department"""
    dept_data = DepartmentCreate(
        name="دپارتمان تست",
        code="TEST-DEPT",
        is_active=True
    )
    dept = department_service.create_department(test_db, dept_data)
    return dept


@pytest.fixture
def test_ticket_data(test_db, test_user_with_token):
    """Create a test ticket"""
    token, user = test_user_with_token
    ticket_data = TicketCreate(
        title="تیکت تست API",
        description="توضیحات تیکت تست",
        category=TicketCategory.SOFTWARE,
        priority=TicketPriority.HIGH
    )
    ticket = ticket_service.create_ticket(test_db, ticket_data, user.id)
    return ticket, token, user


class TestAuthenticationAPI:
    """تست‌های API احراز هویت"""
    
    def test_login_success(self, test_db):
        """تست ورود موفق"""
        # ایجاد کاربر
        user_data = UserCreate(
            username="logintest",
            full_name="Login Test",
            password="loginpass123",
            role=UserRole.USER,
            language=Language.FA
        )
        user_service.create_user(test_db, user_data)
        
        # تست ورود
        response = client.post(
            "/api/auth/login",
            data={"username": "logintest", "password": "loginpass123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" in data
    
    def test_login_invalid_credentials(self, test_db):
        """تست ورود با اطلاعات نادرست"""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent", "password": "wrongpass"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_user_with_token):
        """تست دریافت اطلاعات کاربر فعلی"""
        token, user = test_user_with_token
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "apitest"
        assert data["id"] == user.id
    
    def test_unauthorized_access(self):
        """تست دسترسی بدون احراز هویت"""
        response = client.get("/api/tickets")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """تست با توکن نامعتبر"""
        response = client.get(
            "/api/tickets",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401


class TestTicketsAPI:
    """تست‌های API تیکت‌ها"""
    
    def test_create_ticket(self, test_user_with_token):
        """تست ایجاد تیکت"""
        token, user = test_user_with_token
        
        ticket_data = {
            "title": "تیکت تست API",
            "description": "توضیحات تست",
            "category": "software",
            "priority": "high"
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
        assert data["user_id"] == user.id
        assert data["status"] == "pending"
        assert data["category"] == "software"
        assert data["priority"] == "high"
    
    def test_get_tickets_list(self, test_user_with_token, test_ticket_data):
        """تست دریافت لیست تیکت‌ها"""
        token, user = test_user_with_token
        
        response = client.get(
            "/api/tickets",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["items"], list)
    
    def test_get_ticket_by_id(self, test_user_with_token, test_ticket_data):
        """تست دریافت تیکت با ID"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        response = client.get(
            f"/api/tickets/{ticket.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket.id
        assert data["ticket_number"] == ticket.ticket_number
    
    def test_update_ticket_status(self, test_user_with_token, test_ticket_data):
        """تست به‌روزرسانی وضعیت تیکت"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        response = client.patch(
            f"/api/tickets/{ticket.id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
    
    def test_assign_ticket(self, test_admin_with_token, test_ticket_data):
        """تست تخصیص تیکت"""
        admin_token, admin = test_admin_with_token
        ticket, _, _ = test_ticket_data
        
        response = client.patch(
            f"/api/tickets/{ticket.id}/assign",
            json={"assigned_to_id": admin.id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to_id"] == admin.id
        assert data["status"] == "in_progress"
    
    def test_get_tickets_with_filters(self, test_user_with_token, test_ticket_data):
        """تست دریافت تیکت‌ها با فیلتر"""
        token, user = test_user_with_token
        
        # فیلتر بر اساس وضعیت
        response = client.get(
            "/api/tickets?status=pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # فیلتر بر اساس اولویت
        response = client.get(
            "/api/tickets?priority=high",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # فیلتر بر اساس دسته‌بندی
        response = client.get(
            "/api/tickets?category=software",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
    
    def test_user_can_only_see_own_tickets(self, test_db, test_user_with_token):
        """تست که کاربر فقط تیکت‌های خود را می‌بیند"""
        token1, user1 = test_user_with_token
        
        # ایجاد کاربر دوم
        user2_data = UserCreate(
            username="user2",
            full_name="User 2",
            password="pass123",
            role=UserRole.USER,
            language=Language.FA
        )
        user2 = user_service.create_user(test_db, user2_data)
        token2 = create_access_token(data={"sub": user2.username, "user_id": user2.id, "role": user2.role.value})
        
        # ایجاد تیکت برای کاربر 1
        ticket1_data = TicketCreate(
            title="تیکت کاربر 1",
            description="توضیحات",
            category=TicketCategory.SOFTWARE,
            priority=TicketPriority.MEDIUM
        )
        ticket1 = ticket_service.create_ticket(test_db, ticket1_data, user1.id)
        
        # ایجاد تیکت برای کاربر 2
        ticket2_data = TicketCreate(
            title="تیکت کاربر 2",
            description="توضیحات",
            category=TicketCategory.INTERNET,
            priority=TicketPriority.LOW
        )
        ticket2 = ticket_service.create_ticket(test_db, ticket2_data, user2.id)
        
        # کاربر 1 باید فقط تیکت خود را ببیند
        response = client.get(
            "/api/tickets",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 200
        data = response.json()
        ticket_ids = [t["id"] for t in data["items"]]
        assert ticket1.id in ticket_ids
        assert ticket2.id not in ticket_ids


class TestCommentsAPI:
    """تست‌های API کامنت‌ها"""
    
    def test_create_comment(self, test_user_with_token, test_ticket_data):
        """تست ایجاد کامنت"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        comment_data = {
            "ticket_id": ticket.id,
            "comment": "این یک کامنت تست است",
            "is_internal": False
        }
        
        response = client.post(
            "/api/comments",
            json=comment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["comment"] == "این یک کامنت تست است"
        assert data["ticket_id"] == ticket.id
        assert data["user_id"] == user.id
        assert data["is_internal"] is False
    
    def test_get_ticket_comments(self, test_user_with_token, test_ticket_data):
        """تست دریافت کامنت‌های تیکت"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        # ایجاد چند کامنت
        for i in range(3):
            comment_data = {
                "ticket_id": ticket.id,
                "comment": f"کامنت {i}",
                "is_internal": False
            }
            client.post(
                "/api/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # دریافت کامنت‌ها
        response = client.get(
            f"/api/comments/ticket/{ticket.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3


class TestBranchesAPI:
    """تست‌های API شعب"""
    
    def test_get_branches_list(self, test_admin_with_token):
        """تست دریافت لیست شعب"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/branches",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_branch_admin_only(self, test_admin_with_token):
        """تست ایجاد شعبه (فقط ادمین)"""
        token, admin = test_admin_with_token
        
        branch_data = {
            "name": "شعبه جدید",
            "name_en": "New Branch",
            "code": "NEW",
            "is_active": True
        }
        
        response = client.post(
            "/api/branches",
            json=branch_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "شعبه جدید"
        assert data["code"] == "NEW"
    
    def test_user_cannot_create_branch(self, test_user_with_token):
        """تست که کاربر عادی نمی‌تواند شعبه ایجاد کند"""
        token, user = test_user_with_token
        
        branch_data = {
            "name": "شعبه جدید",
            "name_en": "New Branch",
            "code": "NEW",
            "is_active": True
        }
        
        response = client.post(
            "/api/branches",
            json=branch_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


class TestDepartmentsAPI:
    """تست‌های API دپارتمان‌ها"""
    
    def test_get_departments_list(self, test_admin_with_token):
        """تست دریافت لیست دپارتمان‌ها"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/departments",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_department_admin_only(self, test_admin_with_token):
        """تست ایجاد دپارتمان (فقط ادمین)"""
        token, admin = test_admin_with_token
        
        dept_data = {
            "name": "دپارتمان جدید",
            "code": "NEW-DEPT",
            "is_active": True
        }
        
        response = client.post(
            "/api/departments",
            json=dept_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "دپارتمان جدید"
        assert data["code"] == "NEW-DEPT"


class TestSLAAPI:
    """تست‌های API SLA"""
    
    def test_get_sla_rules(self, test_admin_with_token):
        """تست دریافت لیست قوانین SLA"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/sla",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_sla_rule_admin_only(self, test_admin_with_token):
        """تست ایجاد قانون SLA (فقط ادمین)"""
        token, admin = test_admin_with_token
        
        sla_data = {
            "name": "SLA تست",
            "description": "قانون SLA برای تست",
            "priority": "high",
            "response_time_minutes": 60,
            "resolution_time_minutes": 240,
            "is_active": True
        }
        
        response = client.post(
            "/api/sla",
            json=sla_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "SLA تست"
        assert data["response_time_minutes"] == 60
    
    def test_get_sla_logs_admin_only(self, test_admin_with_token, test_db, test_ticket_data):
        """تست دریافت لاگ‌های SLA (فقط ادمین)"""
        token, admin = test_admin_with_token
        ticket, _, _ = test_ticket_data
        
        # ایجاد قانون SLA
        sla_rule = SLARule(
            name="SLA تست",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True
        )
        test_db.add(sla_rule)
        test_db.commit()
        test_db.refresh(sla_rule)
        
        response = client.get(
            "/api/sla/logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestReportsAPI:
    """تست‌های API گزارش‌ها"""
    
    def test_get_overview_report(self, test_admin_with_token):
        """تست دریافت گزارش کلی"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/reports/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tickets" in data
        assert "open_tickets" in data
    
    def test_get_sla_compliance_report(self, test_admin_with_token):
        """تست دریافت گزارش رعایت SLA"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/reports/sla-compliance",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tickets_with_sla" in data
        assert "response_on_time" in data


class TestCustomFieldsAPI:
    """تست‌های API فیلدهای سفارشی"""
    
    def test_get_custom_fields_admin_only(self, test_admin_with_token):
        """تست دریافت لیست فیلدهای سفارشی (فقط ادمین)"""
        token, admin = test_admin_with_token
        
        response = client.get(
            "/api/custom-fields",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_custom_field_admin_only(self, test_admin_with_token):
        """تست ایجاد فیلد سفارشی (فقط ادمین)"""
        token, admin = test_admin_with_token
        
        field_data = {
            "name": "test_field",
            "label": "فیلد تست",
            "field_type": "text",
            "category": "software",
            "is_active": True
        }
        
        response = client.post(
            "/api/custom-fields",
            json=field_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_field"
        assert data["field_type"] == "text"


class TestTimeTrackerAPI:
    """تست‌های API Time Tracker"""
    
    def test_start_time_log(self, test_user_with_token, test_ticket_data):
        """تست شروع ثبت زمان"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        response = client.post(
            "/api/time-tracker/start",
            json={
                "ticket_id": ticket.id,
                "description": "شروع کار"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["ticket_id"] == ticket.id
        assert data["user_id"] == user.id
        assert data["start_time"] is not None
    
    def test_get_ticket_time_logs(self, test_user_with_token, test_ticket_data):
        """تست دریافت لاگ‌های زمان تیکت"""
        token, user = test_user_with_token
        ticket, _, _ = test_ticket_data
        
        response = client.get(
            f"/api/time-tracker/ticket/{ticket.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

