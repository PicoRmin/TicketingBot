"""
Automation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import AutomationRule, User
from app.schemas.automation_rule import (
    AutomationRuleCreate,
    AutomationRuleUpdate,
    AutomationRuleResponse
)
from app.api.deps import get_current_active_user, require_admin
from app.services.automation_service import (
    create_automation_rule,
    get_automation_rule,
    list_automation_rules,
    update_automation_rule,
    delete_automation_rule,
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_automation_rule(
    request: Request,
    rule_data: AutomationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new automation rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    # Validate rule_type
    valid_types = ["auto_assign", "auto_close", "auto_notify"]
    if rule_data.rule_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("automation.invalid_type", lang) or f"نوع قانون باید یکی از {', '.join(valid_types)} باشد."
        )
    
    # Check if name already exists
    existing = db.query(AutomationRule).filter(AutomationRule.name == rule_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("automation.name_exists", lang) or f"نام قانون '{rule_data.name}' قبلاً استفاده شده است."
        )
    
    rule = create_automation_rule(db, rule_data)
    return rule


@router.get("", response_model=list[AutomationRuleResponse])
async def get_automation_rules(
    request: Request,
    page: int = Query(1, ge=1, description="شماره صفحه"),
    page_size: int = Query(50, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    rule_type: Optional[str] = Query(None, description="فیلتر بر اساس نوع قانون"),
    is_active: Optional[bool] = Query(None, description="فیلتر بر اساس وضعیت"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of automation rules"""
    skip = (page - 1) * page_size
    rules, total = list_automation_rules(db, skip=skip, limit=page_size, rule_type=rule_type, is_active=is_active)
    return rules


@router.get("/{rule_id}", response_model=AutomationRuleResponse)
async def get_automation_rule_by_id(
    request: Request,
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get automation rule by ID"""
    rule = get_automation_rule(db, rule_id)
    if not rule:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("automation.not_found", lang) or "قانون اتوماسیون یافت نشد."
        )
    return rule


@router.put("/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule_by_id(
    request: Request,
    rule_id: int,
    rule_data: AutomationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update automation rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    rule = get_automation_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("automation.not_found", lang) or "قانون اتوماسیون یافت نشد."
        )
    
    # Validate rule_type if provided
    if rule_data.rule_type:
        valid_types = ["auto_assign", "auto_close", "auto_notify"]
        if rule_data.rule_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate("automation.invalid_type", lang) or f"نوع قانون باید یکی از {', '.join(valid_types)} باشد."
            )
    
    # Check if new name already exists
    if rule_data.name and rule_data.name != rule.name:
        existing = db.query(AutomationRule).filter(AutomationRule.name == rule_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate("automation.name_exists", lang) or f"نام قانون '{rule_data.name}' قبلاً استفاده شده است."
            )
    
    updated = update_automation_rule(db, rule, rule_data)
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_rule_by_id(
    request: Request,
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete automation rule (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    rule = get_automation_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("automation.not_found", lang) or "قانون اتوماسیون یافت نشد."
        )
    
    success = delete_automation_rule(db, rule)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("common.error", lang)
        )

