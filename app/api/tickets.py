"""
Ticket API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import Ticket, User
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketStatusUpdate,
    TicketAssignUpdate,
    TicketResponse,
    TicketListResponse,
    BulkActionRequest,
    BulkActionResponse
)
from app.core.enums import TicketStatus, TicketCategory, TicketPriority, UserRole
from app.api.deps import get_current_active_user, require_admin, require_roles
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
from app.services.ticket_history_service import (
    create_ticket_history,
    get_ticket_history,
)
from app.schemas.ticket_history import TicketHistoryCreate, TicketHistoryResponse
from app.services.notification_service import notify_ticket_created, notify_ticket_status_changed
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(
    request: Request,
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new ticket
    
    Args:
        request: FastAPI request object
        ticket_data: Ticket creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Created ticket
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating ticket: title={ticket_data.title[:50]}, category={ticket_data.category}, branch_id={ticket_data.branch_id}, user_id={current_user.id}")

        if current_user.role == UserRole.BRANCH_ADMIN:
            lang = resolve_lang(request, current_user)
            if current_user.branch_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=translate("common.forbidden", lang)
                )
            if ticket_data.branch_id and ticket_data.branch_id != current_user.branch_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=translate("common.forbidden", lang)
                )
            ticket_data.branch_id = current_user.branch_id

        # Create ticket
        ticket = create_ticket(db, ticket_data, current_user.id)
        logger.debug(f"Ticket created: id={ticket.id}, ticket_number={ticket.ticket_number}")
        
        # Reload ticket with user relationship using joinedload to ensure proper serialization
        from sqlalchemy.orm import joinedload
        ticket_id = ticket.id  # Store ID before reload
        db.refresh(ticket)  # Refresh to ensure we have latest data
        
        # Reload with user relationship
        ticket_with_user = db.query(Ticket).options(joinedload(Ticket.user)).filter(Ticket.id == ticket_id).first()
        
        if ticket_with_user:
            ticket = ticket_with_user
            # Ensure user is set
            if not ticket.user:
                logger.warning(f"User relationship not loaded for ticket {ticket.id}, setting manually")
                ticket.user = current_user
        else:
            logger.error(f"Ticket {ticket_id} not found after creation!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=translate("ticket.creation_failed", resolve_lang(request, current_user))
            )

        # Log history for ticket creation
        create_ticket_history(
            db,
            TicketHistoryCreate(
                ticket_id=ticket.id,
                status=ticket.status,
                changed_by_id=current_user.id,
                comment="Ticket created",
            ),
        )

        await notify_ticket_created(ticket, db)

        logger.info(f"Ticket created successfully: id={ticket.id}, ticket_number={ticket.ticket_number}, user={ticket.user.username if ticket.user else 'None'}")
        return ticket
    except Exception as e:
        logger.exception(f"Error creating ticket: {e}", exc_info=True)
        lang = resolve_lang(request, current_user)
        error_detail = translate("ticket.creation_failed", lang) or f"خطا در ایجاد تیکت: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    request: Request,
    page: int = Query(1, ge=1, description="شماره صفحه"),
    page_size: int = Query(10, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    status: Optional[TicketStatus] = Query(None, description="فیلتر بر اساس وضعیت"),
    category: Optional[TicketCategory] = Query(None, description="فیلتر بر اساس دسته‌بندی"),
    priority: Optional[TicketPriority] = Query(None, description="فیلتر بر اساس اولویت"),
    branch_id: Optional[int] = Query(None, description="فیلتر بر اساس شعبه (فقط ادمین)"),
    department_id: Optional[int] = Query(None, description="فیلتر بر اساس دپارتمان"),
    assigned_to_id: Optional[int] = Query(None, description="فیلتر بر اساس کارشناس مسئول"),
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
    lang = resolve_lang(request, current_user)

    admin_roles = (UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.REPORT_MANAGER)

    if branch_id and current_user.role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", lang)
        )

    if current_user.role == UserRole.BRANCH_ADMIN:
        if current_user.branch_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang)
            )
        if branch_id and branch_id != current_user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang)
            )
        tickets, total = get_all_tickets(
            db,
            skip=skip,
            limit=page_size,
            status=status,
            category=category,
            priority=priority,
            branch_id=current_user.branch_id,
            department_id=department_id,
            assigned_to_id=assigned_to_id,
        )
    elif current_user.role in admin_roles:
        tickets, total = get_all_tickets(
            db,
            skip=skip,
            limit=page_size,
            status=status,
            category=category,
            priority=priority,
            branch_id=branch_id,
            department_id=department_id,
            assigned_to_id=assigned_to_id,
        )
    else:
        tickets, total = get_user_tickets(
            db, current_user.id, skip=skip, limit=page_size, status=status, category=category, priority=priority
        )
    
    # Load relationships for each ticket
    from sqlalchemy.orm import joinedload
    for ticket in tickets:
        if not ticket.user:
            ticket.user = db.query(User).filter(User.id == ticket.user_id).first()
        if ticket.assigned_to_id and not ticket.assigned_to:
            ticket.assigned_to = db.query(User).filter(User.id == ticket.assigned_to_id).first()
    
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
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.BRANCH_ADMIN, UserRole.IT_SPECIALIST))
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
    
    if current_user.role == UserRole.BRANCH_ADMIN:
        if current_user.branch_id is None or ticket.branch_id != current_user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", resolve_lang(request, current_user))
            )
    
    previous_status = ticket.status
    updated_ticket = update_ticket_status(db, ticket, status_data.status)
    
    # Create history entry
    from app.schemas.ticket_history import TicketHistoryCreate
    create_ticket_history(
        db,
        TicketHistoryCreate(
            ticket_id=updated_ticket.id,
            status=updated_ticket.status,
            changed_by_id=current_user.id,
            comment=None,
        ),
    )
    await notify_ticket_status_changed(updated_ticket, previous_status, db)
    return updated_ticket


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    request: Request,
    ticket_id: int,
    assign_data: TicketAssignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.BRANCH_ADMIN, UserRole.IT_SPECIALIST))
):
    """
    Assign ticket to a specialist
    
    Args:
        ticket_id: Ticket ID
        assign_data: Assignment data (assigned_to_id)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Updated ticket
        
    Raises:
        HTTPException: If ticket or user not found
    """
    lang = resolve_lang(request, current_user)
    
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang) or "تیکت یافت نشد."
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", lang)
        )
    
    # Validate assigned user exists
    assigned_user = db.query(User).filter(User.id == assign_data.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("users.not_found", lang) or "کاربر یافت نشد."
        )
    
    # Check if user is active
    if not assigned_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("users.inactive_user", lang) or "کاربر غیرفعال است."
        )
    
    # Update ticket assignment
    previous_assigned_to_id = ticket.assigned_to_id
    ticket.assigned_to_id = assign_data.assigned_to_id
    db.commit()
    db.refresh(ticket)
    
    # Load assigned_to relationship
    if ticket.assigned_to_id:
        ticket.assigned_to = db.query(User).filter(User.id == ticket.assigned_to_id).first()
    
    # Create history entry
    from app.schemas.ticket_history import TicketHistoryCreate
    from app.services.ticket_history_service import create_ticket_history
    
    assignment_comment = f"تیکت به {assigned_user.full_name} تخصیص داده شد."
    if previous_assigned_to_id:
        previous_user = db.query(User).filter(User.id == previous_assigned_to_id).first()
        if previous_user:
            assignment_comment = f"تیکت از {previous_user.full_name} به {assigned_user.full_name} منتقل شد."
    
    create_ticket_history(
        db,
        TicketHistoryCreate(
            ticket_id=ticket.id,
            status=ticket.status,
            changed_by_id=current_user.id,
            comment=assignment_comment,
        ),
    )
    
    return ticket


@router.patch("/{ticket_id}/unassign", response_model=TicketResponse)
async def unassign_ticket(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.BRANCH_ADMIN, UserRole.IT_SPECIALIST))
):
    """
    Unassign ticket (remove assignment)
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        TicketResponse: Updated ticket
    """
    lang = resolve_lang(request, current_user)
    
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang) or "تیکت یافت نشد."
        )
    
    # Check access
    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", lang)
        )
    
    # Remove assignment
    previous_assigned_to_id = ticket.assigned_to_id
    ticket.assigned_to_id = None
    db.commit()
    db.refresh(ticket)
    
    # Create history entry
    from app.schemas.ticket_history import TicketHistoryCreate
    from app.services.ticket_history_service import create_ticket_history
    
    if previous_assigned_to_id:
        previous_user = db.query(User).filter(User.id == previous_assigned_to_id).first()
        if previous_user:
            unassign_comment = f"تیکت از {previous_user.full_name} خارج شد."
            create_ticket_history(
                db,
                TicketHistoryCreate(
                    ticket_id=ticket.id,
                    status=ticket.status,
                    changed_by_id=current_user.id,
                    comment=unassign_comment,
                ),
            )
    
    return ticket


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


@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
async def list_ticket_history(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return chronological history for a ticket."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )

    if not can_user_access_ticket(current_user, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )

    history = get_ticket_history(db, ticket_id)
    return history


@router.post("/bulk-action", response_model=BulkActionResponse)
async def bulk_action_tickets(
    request: Request,
    bulk_data: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk actions on tickets (Admin only)
    
    Actions:
    - status: Change status of multiple tickets
    - assign: Assign multiple tickets to a specialist
    - unassign: Unassign multiple tickets
    - delete: Delete multiple tickets
    """
    lang = resolve_lang(request, current_user)
    success_count = 0
    failed_count = 0
    failed_ids = []
    
    for ticket_id in bulk_data.ticket_ids:
        try:
            ticket = get_ticket(db, ticket_id)
            if not ticket:
                failed_count += 1
                failed_ids.append(ticket_id)
                continue
            
            # Check access
            if not can_user_access_ticket(current_user, ticket):
                failed_count += 1
                failed_ids.append(ticket_id)
                continue
            
            if bulk_data.action == "status":
                if not bulk_data.status:
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    continue
                previous_status = ticket.status
                update_ticket_status(db, ticket, bulk_data.status)
                # Create history
                create_ticket_history(
                    db,
                    TicketHistoryCreate(
                        ticket_id=ticket.id,
                        status=bulk_data.status,
                        changed_by_id=current_user.id,
                        comment=f"تغییر وضعیت از {previous_status.value} به {bulk_data.status.value} (Bulk Action)",
                    ),
                )
                # Notify
                await notify_ticket_status_changed(ticket, previous_status, db)
                
            elif bulk_data.action == "assign":
                if not bulk_data.assigned_to_id:
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    continue
                from app.services.user_service import get_user
                assignee = get_user(db, bulk_data.assigned_to_id)
                if not assignee:
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    continue
                ticket.assigned_to_id = bulk_data.assigned_to_id
                db.commit()
                db.refresh(ticket)
                # Create history
                create_ticket_history(
                    db,
                    TicketHistoryCreate(
                        ticket_id=ticket.id,
                        status=ticket.status,
                        changed_by_id=current_user.id,
                        comment=f"تخصیص به {assignee.full_name} (Bulk Action)",
                    ),
                )
                
            elif bulk_data.action == "unassign":
                ticket.assigned_to_id = None
                db.commit()
                db.refresh(ticket)
                # Create history
                create_ticket_history(
                    db,
                    TicketHistoryCreate(
                        ticket_id=ticket.id,
                        status=ticket.status,
                        changed_by_id=current_user.id,
                        comment="حذف تخصیص (Bulk Action)",
                    ),
                )
                
            elif bulk_data.action == "delete":
                from app.services.ticket_service import delete_ticket
                if not delete_ticket(db, ticket):
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    continue
            else:
                failed_count += 1
                failed_ids.append(ticket_id)
                continue
            
            success_count += 1
            
        except Exception as e:
            db.rollback()
            failed_count += 1
            failed_ids.append(ticket_id)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Bulk action error for ticket {ticket_id}: {e}")
    
    return BulkActionResponse(
        success_count=success_count,
        failed_count=failed_count,
        failed_ids=failed_ids
    )

