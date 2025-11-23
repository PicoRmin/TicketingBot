"""
SLA API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import SLARule, User
from app.schemas.sla import (
    SLARuleCreate,
    SLARuleUpdate,
    SLARuleResponse,
    SLALogResponse
)
from app.api.deps import get_current_active_user, require_admin
from app.services.sla_service import (
    create_sla_rule,
    get_sla_rule,
    list_sla_rules,
    update_sla_rule,
    delete_sla_rule,
    get_ticket_sla_log,
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=SLARuleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_sla_rule(
    request: Request,
    sla_data: SLARuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new SLA rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    # Check if name already exists
    existing = db.query(SLARule).filter(SLARule.name == sla_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("sla.name_exists", lang) or f"نام قانون SLA '{sla_data.name}' قبلاً استفاده شده است."
        )
    
    sla_rule = create_sla_rule(db, sla_data)
    return sla_rule


@router.get("", response_model=list[SLARuleResponse])
async def get_sla_rules(
    request: Request,
    page: int = Query(1, ge=1, description="شماره صفحه"),
    page_size: int = Query(50, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    is_active: Optional[bool] = Query(None, description="فیلتر بر اساس وضعیت"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of SLA rules"""
    skip = (page - 1) * page_size
    rules, total = list_sla_rules(db, skip=skip, limit=page_size, is_active=is_active)
    return rules


@router.get("/{sla_id}", response_model=SLARuleResponse)
async def get_sla_rule_by_id(
    request: Request,
    sla_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA rule by ID"""
    sla_rule = get_sla_rule(db, sla_id)
    if not sla_rule:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("sla.not_found", lang) or "قانون SLA یافت نشد."
        )
    return sla_rule


@router.put("/{sla_id}", response_model=SLARuleResponse)
async def update_sla_rule_by_id(
    request: Request,
    sla_id: int,
    sla_data: SLARuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update SLA rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    sla_rule = get_sla_rule(db, sla_id)
    if not sla_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("sla.not_found", lang) or "قانون SLA یافت نشد."
        )
    
    # Check if new name already exists
    if sla_data.name and sla_data.name != sla_rule.name:
        existing = db.query(SLARule).filter(SLARule.name == sla_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate("sla.name_exists", lang) or f"نام قانون SLA '{sla_data.name}' قبلاً استفاده شده است."
            )
    
    updated = update_sla_rule(db, sla_rule, sla_data)
    return updated


@router.delete("/{sla_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sla_rule_by_id(
    request: Request,
    sla_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete SLA rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    sla_rule = get_sla_rule(db, sla_id)
    if not sla_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("sla.not_found", lang) or "قانون SLA یافت نشد."
        )
    
    success = delete_sla_rule(db, sla_rule)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("common.error", lang)
        )


@router.get("/ticket/{ticket_id}", response_model=SLALogResponse)
async def get_ticket_sla(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA log for a ticket"""
    lang = resolve_lang(request, current_user)
    
    sla_log = get_ticket_sla_log(db, ticket_id)
    if not sla_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("sla.log_not_found", lang) or "لاگ SLA برای این تیکت یافت نشد."
        )
    return sla_log


