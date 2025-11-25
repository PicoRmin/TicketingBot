"""
Pytest configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, Ticket, Branch, Department
from app.core.enums import UserRole, Language, TicketCategory, TicketStatus, TicketPriority
from app.core.security import get_password_hash
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ticketing.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        username="testuser",
        full_name="کاربر تست",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.USER,
        language=Language.FA,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db):
    """Create a test admin user"""
    admin = User(
        username="admin",
        full_name="مدیر سیستم",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        language=Language.FA,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_branch(db):
    """Create a test branch"""
    branch = Branch(
        name="شعبه تست",
        name_en="Test Branch",
        code="TEST",
        is_active=True
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@pytest.fixture
def test_department(db):
    """Create a test department"""
    dept = Department(
        name="دپارتمان تست",
        code="TEST-DEPT",
        is_active=True
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@pytest.fixture
def test_ticket(db, test_user):
    """Create a test ticket"""
    ticket = Ticket(
        ticket_number="T-20250101-0001",
        title="تیکت تست",
        description="این یک تیکت تستی است",
        category=TicketCategory.SOFTWARE,
        status=TicketStatus.PENDING,
        priority=TicketPriority.MEDIUM,
        user_id=test_user.id
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

