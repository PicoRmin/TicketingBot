"""
Ticket service for business logic
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from app.models import Ticket, User
from app.core.enums import TicketStatus, TicketCategory, TicketPriority, UserRole
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
    import logging
    from app.models import Branch
    
    logger = logging.getLogger(__name__)
    
    try:
        ticket_number = generate_ticket_number(db)
        logger.debug(f"Generated ticket number: {ticket_number}")
        
        # Validate branch_id if provided
        branch_id = ticket_data.branch_id
        logger.debug(f"Original branch_id: {branch_id}")
        
        if branch_id is not None and branch_id <= 0:
            logger.debug(f"branch_id {branch_id} is <= 0, setting to None")
            branch_id = None
        elif branch_id is not None:
            # Check if branch exists
            branch = db.query(Branch).filter(Branch.id == branch_id).first()
            if not branch:
                logger.warning(f"Branch with id {branch_id} not found, setting to None")
                branch_id = None
            else:
                logger.debug(f"Branch found: {branch.name}")
        
        logger.debug(f"Final branch_id: {branch_id}")
        
        # Validate department_id if provided
        department_id = ticket_data.department_id
        if department_id is not None and department_id <= 0:
            department_id = None
        elif department_id is not None:
            from app.models import Department
            department = db.query(Department).filter(Department.id == department_id).first()
            if not department:
                logger.warning(f"Department with id {department_id} not found, setting to None")
                department_id = None
        
        # Determine priority (use provided or auto-detect)
        priority = ticket_data.priority
        if priority is None:
            priority = _auto_determine_priority(ticket_data.title, ticket_data.description)
        
        ticket = Ticket(
            ticket_number=ticket_number,
            title=ticket_data.title,
            description=ticket_data.description,
            category=ticket_data.category,
            status=TicketStatus.PENDING,
            priority=priority,
            user_id=user_id,
            branch_id=branch_id,
            department_id=department_id
        )
        
        logger.debug(f"Creating ticket: {ticket}")
        db.add(ticket)
        db.commit()
        logger.debug("Ticket committed to database")
        
        db.refresh(ticket)
        logger.debug(f"Ticket refreshed: id={ticket.id}, ticket_number={ticket.ticket_number}")
        
        # Create SLA log if matching rule found
        try:
            from app.services.sla_service import find_matching_sla_rule, create_sla_log
            sla_rule = find_matching_sla_rule(db, priority, ticket_data.category, department_id)
            if sla_rule:
                logger.debug(f"Found matching SLA rule: {sla_rule.name}")
                create_sla_log(db, ticket, sla_rule)
                logger.debug("SLA log created successfully")
        except Exception as e:
            logger.warning(f"Failed to create SLA log: {e}")
            # Don't fail ticket creation if SLA fails
        
        # Auto-assign ticket if no manual assignment
        if ticket.assigned_to_id is None:
            try:
                from app.services.automation_service import auto_assign_ticket
                assigned_user = auto_assign_ticket(db, ticket)
                if assigned_user:
                    logger.debug(f"Auto-assigned ticket {ticket.id} to user {assigned_user.username}")
                    db.refresh(ticket)
            except Exception as e:
                logger.warning(f"Failed to auto-assign ticket: {e}")
                # Don't fail ticket creation if auto-assign fails
        
        return ticket
    except Exception as e:
        logger.exception(f"Error in create_ticket: {e}")
        db.rollback()
        raise


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


def _auto_determine_priority(title: str, description: str) -> TicketPriority:
    """
    Auto-determine ticket priority based on title and description
    
    Args:
        title: Ticket title
        description: Ticket description
        
    Returns:
        TicketPriority: Determined priority
    """
    text = (title + " " + description).lower()
    
    # Critical keywords
    critical_keywords = ["قطع کامل", "کار نمی‌کند", "متوقف شده", "down", "not working", "stopped", "critical"]
    if any(keyword in text for keyword in critical_keywords):
        return TicketPriority.CRITICAL
    
    # High keywords
    high_keywords = ["مشکل دارد", "کند است", "has problem", "slow", "error", "خطا"]
    if any(keyword in text for keyword in high_keywords):
        return TicketPriority.HIGH
    
    # Low keywords
    low_keywords = ["درخواست", "سوال", "راهنمایی", "request", "question", "help", "پیشنهاد", "suggestion"]
    if any(keyword in text for keyword in low_keywords):
        return TicketPriority.LOW
    
    # Default to Medium
    return TicketPriority.MEDIUM


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
    if ticket_data.priority is not None:
        ticket.priority = ticket_data.priority
    if ticket_data.department_id is not None:
        # Validate department exists
        if ticket_data.department_id > 0:
            from app.models import Department
            department = db.query(Department).filter(Department.id == ticket_data.department_id).first()
            if department:
                ticket.department_id = ticket_data.department_id
            else:
                ticket.department_id = None
        else:
            ticket.department_id = None
    if ticket_data.assigned_to_id is not None:
        # Validate user exists
        if ticket_data.assigned_to_id > 0:
            assigned_user = db.query(User).filter(User.id == ticket_data.assigned_to_id).first()
            if assigned_user:
                ticket.assigned_to_id = ticket_data.assigned_to_id
            else:
                ticket.assigned_to_id = None
        else:
            ticket.assigned_to_id = None
    if ticket_data.estimated_resolution_hours is not None:
        ticket.estimated_resolution_hours = ticket_data.estimated_resolution_hours
    if ticket_data.satisfaction_rating is not None:
        ticket.satisfaction_rating = ticket_data.satisfaction_rating
    if ticket_data.satisfaction_comment is not None:
        ticket.satisfaction_comment = ticket_data.satisfaction_comment
    if ticket_data.cost is not None:
        ticket.cost = ticket_data.cost
    
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
    previous_status = ticket.status
    ticket.status = new_status
    
    # Update timestamps for status transitions
    if new_status == TicketStatus.IN_PROGRESS and ticket.first_response_at is None:
        ticket.first_response_at = datetime.utcnow()
    if new_status == TicketStatus.RESOLVED and ticket.resolved_at is None:
        ticket.resolved_at = datetime.utcnow()
        # Calculate actual resolution hours
        if ticket.created_at:
            delta = ticket.resolved_at - ticket.created_at
            ticket.actual_resolution_hours = int(delta.total_seconds() / 3600)
    if new_status == TicketStatus.CLOSED and ticket.closed_at is None:
        ticket.closed_at = datetime.utcnow()
        # Calculate actual resolution hours if not already calculated
        if ticket.actual_resolution_hours is None and ticket.created_at:
            delta = ticket.closed_at - ticket.created_at
            ticket.actual_resolution_hours = int(delta.total_seconds() / 3600)
    
    db.commit()
    db.refresh(ticket)
    
    # Update SLA log status
    try:
        from app.services.sla_service import get_ticket_sla_log, update_sla_log_status
        sla_log = get_ticket_sla_log(db, ticket.id)
        if sla_log:
            update_sla_log_status(db, sla_log, ticket)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to update SLA log: {e}")
        # Don't fail status update if SLA update fails
    
    return ticket


def get_user_tickets(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    category: Optional[TicketCategory] = None,
    priority: Optional[TicketPriority] = None
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
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    total = query.count()
    tickets = query.order_by(
        Ticket.priority.asc(),
        Ticket.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return tickets, total


def get_all_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    category: Optional[TicketCategory] = None,
    priority: Optional[TicketPriority] = None,
    user_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    department_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    ticket_number: Optional[str] = None
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
    if priority:
        query = query.filter(Ticket.priority == priority)
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    if branch_id:
        query = query.filter(Ticket.branch_id == branch_id)
    if department_id:
        query = query.filter(Ticket.department_id == department_id)
    if assigned_to_id:
        query = query.filter(Ticket.assigned_to_id == assigned_to_id)
    if date_from:
        query = query.filter(Ticket.created_at >= date_from)
    if date_to:
        # Add one day to include the entire end date
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(Ticket.created_at < date_to_end)
    if ticket_number:
        query = query.filter(Ticket.ticket_number.ilike(f"%{ticket_number}%"))
    
    total = query.count()
    # Order by priority (critical first) then by created_at
    tickets = query.order_by(
        Ticket.priority.asc(),  # Critical=1, High=2, Medium=3, Low=4
        Ticket.created_at.desc()
    ).offset(skip).limit(limit).all()
    
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
    # Admin-level roles can access all tickets
    if user.role in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.REPORT_MANAGER):
        return True

    # Branch admins limited to their branch
    if user.role == UserRole.BRANCH_ADMIN:
        if user.branch_id is None:
            return False
        return ticket.branch_id == user.branch_id

    # Users can only access their own tickets
    return ticket.user_id == user.id

