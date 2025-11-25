"""
Unit tests for services
"""
import pytest
from datetime import datetime, timedelta
from app.services.ticket_service import (
    create_ticket,
    get_ticket,
    update_ticket_status,
    get_all_tickets
)
from app.services.user_service import create_user
from app.schemas.ticket import TicketCreate
from app.schemas.user import UserCreate
from app.core.enums import TicketStatus, TicketPriority, TicketCategory, UserRole, Language


def test_create_ticket(db, test_user):
    """Test ticket creation service"""
    ticket_data = TicketCreate(
        title="تیکت تست",
        description="توضیحات تست",
        category=TicketCategory.SOFTWARE,
        priority=TicketPriority.HIGH
    )
    
    ticket = create_ticket(db, ticket_data, test_user.id)
    
    assert ticket.id is not None
    assert ticket.title == "تیکت تست"
    assert ticket.user_id == test_user.id
    assert ticket.ticket_number.startswith("T-")
    assert ticket.status == TicketStatus.PENDING


def test_get_ticket(db, test_ticket):
    """Test getting a ticket"""
    ticket = get_ticket(db, test_ticket.id)
    
    assert ticket is not None
    assert ticket.id == test_ticket.id
    assert ticket.ticket_number == test_ticket.ticket_number


def test_update_ticket_status(db, test_ticket):
    """Test updating ticket status"""
    updated = update_ticket_status(db, test_ticket, TicketStatus.IN_PROGRESS)
    
    assert updated.status == TicketStatus.IN_PROGRESS
    assert updated.updated_at is not None


def test_get_all_tickets(db, test_user):
    """Test getting all tickets with filters"""
    # Create multiple tickets
    ticket1_data = TicketCreate(
        title="تیکت 1",
        description="توضیحات 1",
        category=TicketCategory.SOFTWARE,
        priority=TicketPriority.HIGH
    )
    ticket2_data = TicketCreate(
        title="تیکت 2",
        description="توضیحات 2",
        category=TicketCategory.INTERNET,
        priority=TicketPriority.LOW
    )
    
    create_ticket(db, ticket1_data, test_user.id)
    create_ticket(db, ticket2_data, test_user.id)
    
    # Test without filters
    tickets, total = get_all_tickets(db, skip=0, limit=10)
    assert total >= 2
    
    # Test with status filter
    tickets, total = get_all_tickets(
        db,
        skip=0,
        limit=10,
        status=TicketStatus.PENDING
    )
    assert all(t.status == TicketStatus.PENDING for t in tickets)
    
    # Test with priority filter
    tickets, total = get_all_tickets(
        db,
        skip=0,
        limit=10,
        priority=TicketPriority.HIGH
    )
    assert all(t.priority == TicketPriority.HIGH for t in tickets)


def test_create_user(db):
    """Test user creation service"""
    user_data = UserCreate(
        username="newuser",
        full_name="کاربر جدید",
        password="password123",
        role=UserRole.USER,
        language=Language.FA
    )
    
    user = create_user(db, user_data)
    
    assert user.id is not None
    assert user.username == "newuser"
    assert user.role == UserRole.USER


def test_get_user(db, test_user):
    """Test getting user by ID"""
    from app.services.user_service import get_user
    
    user = get_user(db, test_user.id)
    
    assert user is not None
    assert user.username == "testuser"
    assert user.id == test_user.id

