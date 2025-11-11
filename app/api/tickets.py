"""
Ticket API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Ticket, User
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketStatusUpdate,
    TicketResponse,
    TicketListResponse
)
from app.core.enums import TicketStatus, TicketCategory, UserRole
from app.api.deps import get_current_active_user, require_admin
from app.services.ticket_service import (
    create_ticket,
    get_ticket,
    get_ticket_by_number,
    update_ticket,
    update_ticket_status,
    get_user_tickets,
    get_all_tickets,
    can_user_access_ticket,
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new ticket
    
    Args:
        ticket_data: Ticket creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Created ticket
    """
    ticket = create_ticket(db, ticket_data, current_user.id)
    return ticket


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    request: Request,
    page: int = Query(1, ge=1, description="شماره صفحه"),
    page_size: int = Query(10, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    status: Optional[TicketStatus] = Query(None, description="فیلتر بر اساس وضعیت"),
    category: Optional[TicketCategory] = Query(None, description="فیلتر بر اساس دسته‌بندی"),
    branch_id: Optional[int] = Query(None, description="فیلتر بر اساس شعبه (فقط ادمین)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of tickets with pagination and filters
    
    Args:
        page: Page number
        page_size: Items per page
        status: Filter by status
        category: Filter by category
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketListResponse: List of tickets with pagination info
    """
    skip = (page - 1) * page_size
    
    # Admin can see all tickets, users can only see their own
    if current_user.role == UserRole.ADMIN:
        tickets, total = get_all_tickets(
            db, skip=skip, limit=page_size, status=status, category=category, branch_id=branch_id
        )
    else:
        tickets, total = get_user_tickets(
            db, current_user.id, skip=skip, limit=page_size, status=status, category=category
        )
    
    # Load user relationship for each ticket
    for ticket in tickets:
        if not ticket.user:
            ticket.user = db.query(User).filter(User.id == ticket.user_id).first()
    
    total_pages = (total + page_size - 1) // page_size
    
    return TicketListResponse(
        items=tickets,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_by_id(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get ticket by ID
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Ticket details
        
    Raises:
        HTTPException: If ticket not found or user doesn't have access
    """
    ticket = get_ticket(db, ticket_id)
    
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    
    return ticket


@router.get("/number/{ticket_number}", response_model=TicketResponse)
async def get_ticket_by_ticket_number(
    request: Request,
    ticket_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get ticket by ticket number
    
    Args:
        ticket_number: Ticket number (e.g., T-20241111-0001)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Ticket details
        
    Raises:
        HTTPException: If ticket not found or user doesn't have access
    """
    ticket = get_ticket_by_number(db, ticket_number)
    
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket_by_id(
    request: Request,
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update ticket
    
    Args:
        ticket_id: Ticket ID
        ticket_data: Update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Updated ticket
        
    Raises:
        HTTPException: If ticket not found or user doesn't have access
    """
    ticket = get_ticket(db, ticket_id)
    
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    
    # Only admin can change status
    if ticket_data.status is not None and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    
    updated_ticket = update_ticket(db, ticket, ticket_data)
    return updated_ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status_by_id(
    request: Request,
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update ticket status (Admin only)
    
    Args:
        ticket_id: Ticket ID
        status_data: New status
        db: Database session
        current_user: Current admin user
        
    Returns:
        TicketResponse: Updated ticket
        
    Raises:
        HTTPException: If ticket not found
    """
    ticket = get_ticket(db, ticket_id)
    
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    updated_ticket = update_ticket_status(db, ticket, status_data.status)
    return updated_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket_by_id(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete ticket (Admin only)
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        current_user: Current admin user
        
    Raises:
        HTTPException: If ticket not found
    """
    from app.services.ticket_service import delete_ticket
    
    ticket = get_ticket(db, ticket_id)
    
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    success = delete_ticket(db, ticket)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("common.error", resolve_lang(request, current_user))
        )

