"""
Security-focused API tests covering authentication, authorization, and input validation.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal, get_db
from app.core.enums import UserRole, Language, TicketCategory, TicketPriority
from app.schemas.user import UserCreate
from app.schemas.ticket import TicketCreate
from app.services import user_service
from app.services.ticket_service import create_ticket


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure a clean database for every test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _create_user(username: str, role: UserRole) -> None:
    db = SessionLocal()
    try:
        user_service.create_user(
            db,
            UserCreate(
                username=username,
                full_name=username,
                password="Pass123!",
                role=role,
                language=Language.FA,
            ),
        )
    finally:
        db.close()


def _login(username: str, password: str = "Pass123!") -> str:
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_with_invalid_credentials_returns_401():
    """Ensure authentication failures do not leak sensitive info."""
    response = client.post(
        "/api/auth/login",
        data={"username": "unknown", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_protected_endpoint_requires_authentication():
    """Accessing protected endpoints without token should return 401."""
    response = client.get("/api/tickets")
    assert response.status_code == 401


def test_admin_only_endpoint_rejects_regular_user():
    """Regular users must not be able to call admin-only endpoints."""
    _create_user("normal_user", UserRole.USER)
    token = _login("normal_user")

    payload = {
        "name": "شعبه ممنوع",
        "name_en": "Forbidden Branch",
        "code": "FORBIDDEN",
        "is_active": True,
    }
    response = client.post(
        "/api/branches",
        json=payload,
        headers=_headers(token),
    )
    assert response.status_code == 403


def test_user_cannot_access_other_user_ticket():
    """Users should not see tickets belonging to others."""
    _create_user("owner", UserRole.USER)
    _create_user("intruder", UserRole.USER)

    owner_token = _login("owner")
    intruder_token = _login("intruder")

    # Owner creates a ticket
    create_resp = client.post(
        "/api/tickets",
        json={
            "title": "T1",
            "description": "Owner ticket",
            "category": TicketCategory.SOFTWARE.value,
            "priority": TicketPriority.MEDIUM.value,
        },
        headers=_headers(owner_token),
    )
    assert create_resp.status_code == 201
    ticket_id = create_resp.json()["id"]

    # Intruder tries to fetch it
    get_resp = client.get(
        f"/api/tickets/{ticket_id}",
        headers=_headers(intruder_token),
    )
    assert get_resp.status_code == 403


def test_ticket_creation_invalid_category_is_rejected():
    """Input validation should block invalid enum values."""
    _create_user("user_input", UserRole.USER)
    token = _login("user_input")

    payload = {
        "title": "Invalid Category",
        "description": "Attempt with incorrect enum",
        "category": "invalid_category",
    }
    response = client.post(
        "/api/tickets",
        json=payload,
        headers=_headers(token),
    )
    assert response.status_code == 422


def test_sql_like_payload_is_treated_as_plain_text():
    """Ensure malicious-looking payloads are accepted as text and not executed."""
    _create_user("user_sql", UserRole.USER)
    db = SessionLocal()
    try:
        owner = user_service.get_user_by_username(db, "user_sql")
        ticket = create_ticket(
            db,
            TicketCreate(
                title="Safe title",
                description="Legit ticket",
                category=TicketCategory.INTERNET,
                priority=TicketPriority.HIGH,
            ),
            owner.id,
        )
    finally:
        db.close()

    token = _login("user_sql")
    # Attempt to update status with suspicious text in comment
    response = client.post(
        "/api/comments",
        json={
            "ticket_id": ticket.id,
            "comment": "'); DROP TABLE tickets; --",
            "is_internal": False,
        },
        headers=_headers(token),
    )
    # Should be accepted as plain text comment (validation passes)
    assert response.status_code == 201
    assert response.json()["comment"] == "'); DROP TABLE tickets; --"

