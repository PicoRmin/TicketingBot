"""
End-to-end tests covering full ticket lifecycle and Telegram bot API client.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.database import Base, engine, get_db, SessionLocal
from app.core.enums import (
    UserRole,
    Language,
    TicketCategory,
    TicketPriority,
)
from app.schemas.user import UserCreate
from app.schemas.branch import BranchCreate
from app.schemas.department import DepartmentCreate
from app.services import user_service
from app.services.branch_service import create_branch
from app.services.department_service import create_department
from app.telegram_bot.api_client import APIClient


# Override FastAPI dependency to use the same testing session
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def _setup_database():
    """Ensure a clean database for each E2E test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _login(username: str, password: str) -> str:
    """Helper to obtain an access token via the auth endpoint."""
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.e2e
def test_full_ticket_lifecycle_flow():
    """
    Simulate the portal-level journey:
    - Create branch/department, user, and admin
    - User logs in and creates a ticket
    - Admin assigns, works on, comments, and resolves the ticket
    - Validate history, time logs, and final status
    """
    db = SessionLocal()

    # Prepare base data (branch & department used by portal dropdowns)
    branch = create_branch(
        db,
        BranchCreate(
            name="شعبه مرکزی",
            name_en="HQ",
            code="HQ01",
            is_active=True,
        ),
    )
    department = create_department(
        db,
        DepartmentCreate(
            name="فناوری اطلاعات",
            code="IT-DEP",
            is_active=True,
        ),
    )

    # Create portal user and admin
    user_service.create_user(
        db,
        UserCreate(
            username="e2e_user",
            full_name="کاربر تست E2E",
            password="UserPass123!",
            role=UserRole.USER,
            language=Language.FA,
        ),
    )
    user_service.create_user(
        db,
        UserCreate(
            username="e2e_admin",
            full_name="مدیر تست E2E",
            password="AdminPass123!",
            role=UserRole.ADMIN,
            language=Language.FA,
        ),
    )
    db.close()

    user_token = _login("e2e_user", "UserPass123!")
    admin_token = _login("e2e_admin", "AdminPass123!")

    # User creates a ticket via the same endpoint used by the web portal
    ticket_payload = {
        "title": "مشکل اینترنت شعبه مرکزی",
        "description": "سرعت اینترنت بسیار پایین شده و اتصال قطع می‌شود.",
        "category": "internet",
        "priority": TicketPriority.HIGH.value,
        "branch_id": branch.id,
        "department_id": department.id,
    }
    create_resp = client.post(
        "/api/tickets",
        json=ticket_payload,
        headers=_auth_header(user_token),
    )
    assert create_resp.status_code == 201
    ticket = create_resp.json()

    # User fetches ticket list (simulating portal dashboard filters)
    list_resp = client.get(
        "/api/tickets?page=1&limit=10&status=pending",
        headers=_auth_header(user_token),
    )
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    ticket_id = ticket["id"]

    # Admin assigns the ticket to self
    assign_resp = client.patch(
        f"/api/tickets/{ticket_id}/assign",
        json={"assigned_to_id": 2},  # admin user id (created second)
        headers=_auth_header(admin_token),
    )
    assert assign_resp.status_code == 200
    assert assign_resp.json()["assigned_to_id"] == 2

    # Admin moves status to IN_PROGRESS
    status_resp = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
        headers=_auth_header(admin_token),
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "in_progress"

    # Admin starts a time tracker entry
    start_timer = client.post(
        "/api/time-tracker/start",
        json={"ticket_id": ticket_id, "description": "در حال بررسی اتصال"},
        headers=_auth_header(admin_token),
    )
    assert start_timer.status_code == 201
    time_log_id = start_timer.json()["id"]

    # Admin stops the timer with a final note
    stop_timer = client.post(
        f"/api/time-tracker/stop/{time_log_id}",
        json={"description": "مشکل برطرف شد"},
        headers=_auth_header(admin_token),
    )
    assert stop_timer.status_code == 200
    assert stop_timer.json()["duration_minutes"] >= 0

    # Admin adds a public comment
    comment_resp = client.post(
        "/api/comments",
        json={"ticket_id": ticket_id, "comment": "کابل شبکه تعویض شد.", "is_internal": False},
        headers=_auth_header(admin_token),
    )
    assert comment_resp.status_code == 201

    # User confirms the fix and closes the ticket
    close_resp = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "resolved"},
        headers=_auth_header(user_token),
    )
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "resolved"

    # Fetch ticket history to ensure all steps were recorded
    history_resp = client.get(
        f"/api/tickets/{ticket_id}/history",
        headers=_auth_header(admin_token),
    )
    assert history_resp.status_code == 200
    assert len(history_resp.json()) >= 3  # creation, in_progress, resolved

    # Fetch time logs to ensure work diary is captured
    time_logs_resp = client.get(
        f"/api/time-tracker/ticket/{ticket_id}",
        headers=_auth_header(admin_token),
    )
    assert time_logs_resp.status_code == 200
    assert len(time_logs_resp.json()) == 1

    # Final ticket view should reflect resolution
    final_ticket = client.get(
        f"/api/tickets/{ticket_id}",
        headers=_auth_header(user_token),
    )
    assert final_ticket.status_code == 200
    assert final_ticket.json()["status"] == "resolved"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_telegram_api_client_can_login_and_create_ticket():
    """
    Validate Telegram bot API client against the live FastAPI application.
    """
    db = SessionLocal()
    create_branch(
        db,
        BranchCreate(
            name="شعبه غرب",
            name_en="West Branch",
            code="WEST",
            is_active=True,
        ),
    )
    user_service.create_user(
        db,
        UserCreate(
            username="telegram_user",
            full_name="کاربر ربات تلگرام",
            password="BotPass123!",
            role=UserRole.USER,
            language=Language.FA,
        ),
    )
    db.close()

    api_client = APIClient(base_url="http://testserver")
    api_client.client = AsyncClient(app=app, base_url="http://testserver")

    try:
        token = await api_client.login("telegram_user", "BotPass123!")
        assert token

        branches = await api_client.get_branches(token)
        assert branches and isinstance(branches, list)
        branch_id = branches[0]["id"]

        # Create a ticket through the Telegram client
        ticket = await api_client.create_ticket(
            token=token,
            title="درخواست از طریق ربات",
            description="این تیکت برای تست ربات ثبت شده است.",
            category=TicketCategory.SOFTWARE,
            branch_id=branch_id,
            priority=TicketPriority.MEDIUM.value,
        )
        assert ticket is not None

        # Retrieve tickets (simulates /my_tickets flow)
        tickets = await api_client.get_user_tickets(token)
        assert tickets is not None
        assert tickets.get("total", 0) >= 1
    finally:
        await api_client.close()

