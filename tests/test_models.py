"""
Unit tests for database models
"""
import pytest
from app.models import User, Ticket, Branch, Department
from app.core.enums import UserRole, Language, TicketCategory, TicketStatus, TicketPriority
from app.core.security import get_password_hash, verify_password
from datetime import datetime


def test_user_creation(db, test_user):
    """Test user model creation"""
    assert test_user.id is not None
    assert test_user.username == "testuser"
    assert test_user.full_name == "کاربر تست"
    assert test_user.role == UserRole.USER
    assert test_user.is_active is True
    assert verify_password("testpass123", test_user.password_hash)


def test_user_password_hashing(db):
    """Test password hashing"""
    user = User(
        username="hashtest",
        full_name="Test",
        password_hash=get_password_hash("mypassword"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    assert verify_password("mypassword", user.password_hash)
    assert not verify_password("wrongpassword", user.password_hash)


def test_ticket_creation(db, test_user, test_ticket):
    """Test ticket model creation"""
    assert test_ticket.id is not None
    assert test_ticket.ticket_number == "T-20250101-0001"
    assert test_ticket.title == "تیکت تست"
    assert test_ticket.category == TicketCategory.SOFTWARE
    assert test_ticket.status == TicketStatus.PENDING
    assert test_ticket.priority == TicketPriority.MEDIUM
    assert test_ticket.user_id == test_user.id


def test_ticket_user_relationship(db, test_user, test_ticket):
    """Test ticket-user relationship"""
    assert test_ticket.user.id == test_user.id
    assert test_ticket.user.username == test_user.username
    assert test_ticket in test_user.tickets


def test_ticket_status_update(db, test_ticket):
    """Test ticket status update"""
    test_ticket.status = TicketStatus.IN_PROGRESS
    db.commit()
    db.refresh(test_ticket)
    
    assert test_ticket.status == TicketStatus.IN_PROGRESS


def test_branch_creation(db, test_branch):
    """Test branch model creation"""
    assert test_branch.id is not None
    assert test_branch.name == "شعبه تست"
    assert test_branch.code == "TEST"
    assert test_branch.is_active is True


def test_department_creation(db, test_department):
    """Test department model creation"""
    assert test_department.id is not None
    assert test_department.name == "دپارتمان تست"
    assert test_department.code == "TEST-DEPT"
    assert test_department.is_active is True


def test_user_branch_relationship(db, test_user, test_branch):
    """Test user-branch relationship"""
    test_user.branch_id = test_branch.id
    db.commit()
    db.refresh(test_user)
    
    assert test_user.branch.id == test_branch.id
    assert test_user in test_branch.users


