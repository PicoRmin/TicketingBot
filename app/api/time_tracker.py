"""
API endpoints for Time Tracker
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Ticket
from app.api.deps import get_current_active_user
from app.schemas.time_log import TimeLogCreate, TimeLogUpdate, TimeLogResponse, TimeLogSummary
from app.services import time_tracker_service
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang
from app.core.enums import UserRole

router = APIRouter()


@router.post("/start", response_model=TimeLogResponse, status_code=status.HTTP_201_CREATED)
async def start_timer(
    request: Request,
    data: TimeLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    شروع تایمر برای یک تیکت
    """
    lang = resolve_lang(request, current_user)
    
    # بررسی وجود تیکت
    ticket = db.query(Ticket).filter(Ticket.id == data.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    try:
        time_log = time_tracker_service.start_timer(
            db, data.ticket_id, current_user.id, data.description
        )
        
        # Load relationships
        db.refresh(time_log)
        if time_log.user:
            time_log.user = {"id": time_log.user.id, "full_name": time_log.user.full_name, "username": time_log.user.username}
        if time_log.ticket:
            time_log.ticket = {"id": time_log.ticket.id, "ticket_number": time_log.ticket.ticket_number, "title": time_log.ticket.title}
        
        return time_log
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stop/{time_log_id}", response_model=TimeLogResponse)
async def stop_timer(
    request: Request,
    time_log_id: int,
    data: Optional[TimeLogUpdate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    توقف تایمر
    """
    lang = resolve_lang(request, current_user)
    
    try:
        description = data.description if data else None
        time_log = time_tracker_service.stop_timer(
            db, time_log_id, current_user.id, description
        )
        
        # Load relationships
        db.refresh(time_log)
        if time_log.user:
            time_log.user = {"id": time_log.user.id, "full_name": time_log.user.full_name, "username": time_log.user.username}
        if time_log.ticket:
            time_log.ticket = {"id": time_log.ticket.id, "ticket_number": time_log.ticket.ticket_number, "title": time_log.ticket.title}
        
        return time_log
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stop-active", response_model=Optional[TimeLogResponse])
async def stop_active_timer(
    request: Request,
    data: Optional[TimeLogUpdate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    توقف تایمر فعال کاربر
    """
    try:
        description = data.description if data else None
        time_log = time_tracker_service.stop_active_timer(
            db, current_user.id, description
        )
        
        if not time_log:
            return None
        
        # Load relationships
        db.refresh(time_log)
        if time_log.user:
            time_log.user = {"id": time_log.user.id, "full_name": time_log.user.full_name, "username": time_log.user.username}
        if time_log.ticket:
            time_log.ticket = {"id": time_log.ticket.id, "ticket_number": time_log.ticket.ticket_number, "title": time_log.ticket.title}
        
        return time_log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/active", response_model=Optional[TimeLogResponse])
async def get_active_timer(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    دریافت تایمر فعال کاربر
    """
    time_log = time_tracker_service.get_active_timer(db, current_user.id)
    
    if not time_log:
        return None
    
    # Load relationships
    db.refresh(time_log)
    if time_log.user:
        time_log.user = {"id": time_log.user.id, "full_name": time_log.user.full_name, "username": time_log.user.username}
    if time_log.ticket:
        time_log.ticket = {"id": time_log.ticket.id, "ticket_number": time_log.ticket.ticket_number, "title": time_log.ticket.title}
    
    return time_log


@router.get("/ticket/{ticket_id}", response_model=List[TimeLogResponse])
async def get_ticket_time_logs(
    request: Request,
    ticket_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    دریافت Time Logs یک تیکت
    """
    lang = resolve_lang(request, current_user)
    
    # بررسی وجود تیکت
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    # بررسی دسترسی (کاربر باید صاحب تیکت باشد یا کارشناس مسئول یا ادمین)
    if current_user.role not in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.IT_SPECIALIST):
        if ticket.user_id != current_user.id and ticket.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang)
            )
    
    filter_user_id = user_id if current_user.role in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN) else current_user.id
    
    time_logs = time_tracker_service.get_ticket_time_logs(db, ticket_id, filter_user_id)
    
    # Format response
    result = []
    for log in time_logs:
        log_dict = {
            "id": log.id,
            "ticket_id": log.ticket_id,
            "user_id": log.user_id,
            "start_time": log.start_time,
            "end_time": log.end_time,
            "duration_minutes": log.duration_minutes,
            "description": log.description,
            "is_active": log.is_active,
            "created_at": log.created_at,
            "updated_at": log.updated_at,
        }
        if log.user:
            log_dict["user"] = {"id": log.user.id, "full_name": log.user.full_name, "username": log.user.username}
        if log.ticket:
            log_dict["ticket"] = {"id": log.ticket.id, "ticket_number": log.ticket.ticket_number, "title": log.ticket.title}
        result.append(log_dict)
    
    return result


@router.get("/ticket/{ticket_id}/summary", response_model=TimeLogSummary)
async def get_ticket_time_summary(
    request: Request,
    ticket_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    دریافت خلاصه زمان کار روی یک تیکت
    """
    lang = resolve_lang(request, current_user)
    
    # بررسی وجود تیکت
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("tickets.not_found", lang)
        )
    
    filter_user_id = user_id if current_user.role in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN) else None
    
    summary = time_tracker_service.get_ticket_total_time(db, ticket_id, filter_user_id)
    return summary


@router.put("/{time_log_id}", response_model=TimeLogResponse)
async def update_time_log(
    request: Request,
    time_log_id: int,
    data: TimeLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    به‌روزرسانی توضیحات Time Log
    """
    try:
        time_log = time_tracker_service.update_time_log_description(
            db, time_log_id, current_user.id, data.description or ""
        )
        
        # Load relationships
        db.refresh(time_log)
        if time_log.user:
            time_log.user = {"id": time_log.user.id, "full_name": time_log.user.full_name, "username": time_log.user.username}
        if time_log.ticket:
            time_log.ticket = {"id": time_log.ticket.id, "ticket_number": time_log.ticket.ticket_number, "title": time_log.ticket.title}
        
        return time_log
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{time_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_log(
    request: Request,
    time_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    حذف Time Log
    """
    success = time_tracker_service.delete_time_log(db, time_log_id, current_user.id)
    
    if not success:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("common.not_found", lang)
        )
    
    return None

