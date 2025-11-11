"""
Ticket service for business logic
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from app.models import Ticket, User
from app.core.enums import TicketStatus, TicketCategory, UserRole
from app.schemas.ticket import TicketCreate, TicketUpdate


def generate_ticket_number(db: Session) -> str:
    """
    Generate unique ticket number in format: T-YYYYMMDD-####
    
    Args:
        db: Database session
        
    Returns:
        str: Unique ticket number
    """
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"T-{today}-"
    
    # Count tickets created today
    count = db.query(Ticket).filter(
        Ticket.ticket_number.like(f"{prefix}%")
    ).count()
    
    # Generate ticket number with 4-digit zero-padded number
    ticket_number = f"{prefix}{str(count + 1).zfill(4)}"
    
    return ticket_number


def create_ticket(
    db: Session,
    ticket_data: TicketCreate,
    user_id: int
) -> Ticket:
    """
    Create a new ticket
    
    Args:
        db: Database session
        ticket_data: Ticket creation data
        user_id: ID of the user creating the ticket
        
    Returns:
        Ticket: Created ticket
    """
    ticket_number = generate_ticket_number(db)
    
    ticket = Ticket(
        ticket_number=ticket_number,
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category,
        status=TicketStatus.PENDING,
        user_id=user_id
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """
    Get ticket by ID
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        
    Returns:
        Ticket or None
    """
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[Ticket]:
    """
    Get ticket by ticket number
    
    Args:
        db: Database session
        ticket_number: Ticket number
        
    Returns:
        Ticket or None
    """
    return db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()


def update_ticket(
    db: Session,
    ticket: Ticket,
    ticket_data: TicketUpdate
) -> Ticket:
    """
    Update ticket
    
    Args:
        db: Database session
        ticket: Ticket to update
        ticket_data: Update data
        
    Returns:
        Ticket: Updated ticket
    """
    if ticket_data.title is not None:
        ticket.title = ticket_data.title
    if ticket_data.description is not None:
        ticket.description = ticket_data.description
    if ticket_data.category is not None:
        ticket.category = ticket_data.category
    if ticket_data.status is not None:
        ticket.status = ticket_data.status
    
    db.commit()
    db.refresh(ticket)
    
    return ticket


def update_ticket_status(
    db: Session,
    ticket: Ticket,
    new_status: TicketStatus
) -> Ticket:
    """
    Update ticket status
    
    Args:
        db: Database session
        ticket: Ticket to update
        new_status: New status
        
    Returns:
        Ticket: Updated ticket
    """
    ticket.status = new_status
    db.commit()
    db.refresh(ticket)
    
    return ticket


def get_user_tickets(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    category: Optional[TicketCategory] = None
) -> Tuple[List[Ticket], int]:
    """
    Get tickets for a specific user with filters
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (optional)
        category: Filter by category (optional)
        
    Returns:
        Tuple of (tickets list, total count)
    """
    query = db.query(Ticket).filter(Ticket.user_id == user_id)
    
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    return tickets, total


def get_all_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    category: Optional[TicketCategory] = None,
    user_id: Optional[int] = None
) -> Tuple[List[Ticket], int]:
    """
    Get all tickets (for admin) with filters
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (optional)
        category: Filter by category (optional)
        user_id: Filter by user ID (optional)
        
    Returns:
        Tuple of (tickets list, total count)
    """
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    return tickets, total


def delete_ticket(db: Session, ticket: Ticket) -> bool:
    """
    Delete a ticket
    
    Args:
        db: Database session
        ticket: Ticket to delete
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        db.delete(ticket)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def can_user_access_ticket(user: User, ticket: Ticket) -> bool:
    """
    Check if user can access a ticket
    
    Args:
        user: User trying to access
        ticket: Ticket to access
        
    Returns:
        bool: True if user can access
    """
    # Admin can access all tickets
    if user.role == UserRole.ADMIN:
        return True
    
    # User can only access their own tickets
    return ticket.user_id == user.id

