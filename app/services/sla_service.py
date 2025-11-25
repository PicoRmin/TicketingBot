"""
SLA service for business logic
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.models import SLARule, SLALog, Ticket, Department
from app.core.enums import TicketPriority, TicketCategory
from app.schemas.sla import SLARuleCreate, SLARuleUpdate


def find_matching_sla_rule(
    db: Session,
    priority: TicketPriority,
    category: TicketCategory,
    department_id: Optional[int] = None
) -> Optional[SLARule]:
    """
    Find matching SLA rule for a ticket
    
    Priority: More specific rules first
    1. priority + category + department
    2. priority + category
    3. priority + department
    4. category + department
    5. priority only
    6. category only
    7. department only
    8. default (all None)
    """
    # Try most specific first
    query = db.query(SLARule).filter(SLARule.is_active == True)
    
    # Try: priority + category + department
    if department_id:
        rule = query.filter(
            SLARule.priority == priority,
            SLARule.category == category,
            SLARule.department_id == department_id
        ).first()
        if rule:
            return rule
    
    # Try: priority + category
    rule = query.filter(
        SLARule.priority == priority,
        SLARule.category == category,
        SLARule.department_id.is_(None)
    ).first()
    if rule:
        return rule
    
    # Try: priority + department
    if department_id:
        rule = query.filter(
            SLARule.priority == priority,
            SLARule.category.is_(None),
            SLARule.department_id == department_id
        ).first()
        if rule:
            return rule
    
    # Try: category + department
    if department_id:
        rule = query.filter(
            SLARule.priority.is_(None),
            SLARule.category == category,
            SLARule.department_id == department_id
        ).first()
        if rule:
            return rule
    
    # Try: priority only
    rule = query.filter(
        SLARule.priority == priority,
        SLARule.category.is_(None),
        SLARule.department_id.is_(None)
    ).first()
    if rule:
        return rule
    
    # Try: category only
    rule = query.filter(
        SLARule.priority.is_(None),
        SLARule.category == category,
        SLARule.department_id.is_(None)
    ).first()
    if rule:
        return rule
    
    # Try: department only
    if department_id:
        rule = query.filter(
            SLARule.priority.is_(None),
            SLARule.category.is_(None),
            SLARule.department_id == department_id
        ).first()
        if rule:
            return rule
    
    # Try: default (all None)
    rule = query.filter(
        SLARule.priority.is_(None),
        SLARule.category.is_(None),
        SLARule.department_id.is_(None)
    ).first()
    
    return rule


def create_sla_log(
    db: Session,
    ticket: Ticket,
    sla_rule: SLARule
) -> SLALog:
    """Create SLA log for a ticket"""
    now = datetime.utcnow()
    
    target_response_time = now + timedelta(minutes=sla_rule.response_time_minutes)
    target_resolution_time = now + timedelta(minutes=sla_rule.resolution_time_minutes)
    
    sla_log = SLALog(
        ticket_id=ticket.id,
        sla_rule_id=sla_rule.id,
        target_response_time=target_response_time,
        target_resolution_time=target_resolution_time
    )
    
    db.add(sla_log)
    db.commit()
    db.refresh(sla_log)
    
    return sla_log


def update_sla_log_status(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket
) -> SLALog:
    """Update SLA log status based on current ticket state"""
    now = datetime.utcnow()
    
    # Update response status
    if ticket.first_response_at:
        sla_log.actual_response_time = ticket.first_response_at
        if ticket.first_response_at <= sla_log.target_response_time:
            sla_log.response_status = "on_time"
        else:
            sla_log.response_status = "breached"
    else:
        # Check if we're in warning zone
        warning_time = sla_log.target_response_time - timedelta(minutes=sla_log.sla_rule.response_warning_minutes)
        if now >= warning_time and now < sla_log.target_response_time:
            sla_log.response_status = "warning"
        elif now >= sla_log.target_response_time:
            sla_log.response_status = "breached"
    
    # Update resolution status
    if ticket.resolved_at or ticket.closed_at:
        resolution_time = ticket.resolved_at or ticket.closed_at
        sla_log.actual_resolution_time = resolution_time
        if resolution_time <= sla_log.target_resolution_time:
            sla_log.resolution_status = "on_time"
        else:
            sla_log.resolution_status = "breached"
    else:
        # Check if we're in warning zone
        warning_time = sla_log.target_resolution_time - timedelta(minutes=sla_log.sla_rule.resolution_warning_minutes)
        if now >= warning_time and now < sla_log.target_resolution_time:
            sla_log.resolution_status = "warning"
        elif now >= sla_log.target_resolution_time:
            sla_log.resolution_status = "breached"
    
    # Check escalation
    if sla_log.sla_rule.escalation_enabled and sla_log.sla_rule.escalation_after_minutes:
        escalation_time = ticket.created_at + timedelta(minutes=sla_log.sla_rule.escalation_after_minutes)
        if now >= escalation_time and not sla_log.escalated:
            sla_log.escalated = True
            sla_log.escalated_at = now
    
    db.commit()
    db.refresh(sla_log)
    
    return sla_log


def create_sla_rule(db: Session, sla_data: SLARuleCreate) -> SLARule:
    """Create new SLA rule"""
    sla_rule = SLARule(**sla_data.model_dump())
    db.add(sla_rule)
    db.commit()
    db.refresh(sla_rule)
    return sla_rule


def get_sla_rule(db: Session, sla_id: int) -> Optional[SLARule]:
    """Get SLA rule by ID"""
    return db.query(SLARule).filter(SLARule.id == sla_id).first()


def list_sla_rules(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None
) -> Tuple[List[SLARule], int]:
    """List SLA rules with pagination"""
    query = db.query(SLARule)
    if is_active is not None:
        query = query.filter(SLARule.is_active == is_active)
    total = query.count()
    # order_by must be called before offset/limit
    items = query.order_by(SLARule.name).offset(skip).limit(limit).all()
    return items, total


def update_sla_rule(
    db: Session,
    sla_rule: SLARule,
    sla_data: SLARuleUpdate
) -> SLARule:
    """Update SLA rule"""
    update_data = sla_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sla_rule, field, value)
    db.commit()
    db.refresh(sla_rule)
    return sla_rule


def delete_sla_rule(db: Session, sla_rule: SLARule) -> bool:
    """Delete SLA rule"""
    try:
        db.delete(sla_rule)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_ticket_sla_log(db: Session, ticket_id: int) -> Optional[SLALog]:
    """Get SLA log for a ticket"""
    return db.query(SLALog).filter(SLALog.ticket_id == ticket_id).first()


def list_sla_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    ticket_id: Optional[int] = None,
    sla_rule_id: Optional[int] = None,
    response_status: Optional[str] = None,
    resolution_status: Optional[str] = None,
    escalated: Optional[bool] = None
) -> Tuple[List[SLALog], int]:
    """
    لیست لاگ‌های SLA با فیلتر و pagination
    List SLA logs with filters and pagination
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(SLALog).options(
        joinedload(SLALog.ticket),
        joinedload(SLALog.sla_rule)
    )
    
    # اعمال فیلترها
    if ticket_id:
        query = query.filter(SLALog.ticket_id == ticket_id)
    if sla_rule_id:
        query = query.filter(SLALog.sla_rule_id == sla_rule_id)
    if response_status:
        query = query.filter(SLALog.response_status == response_status)
    if resolution_status:
        query = query.filter(SLALog.resolution_status == resolution_status)
    if escalated is not None:
        query = query.filter(SLALog.escalated == escalated)
    
    # شمارش کل
    total = query.count()
    
    # مرتب‌سازی و pagination
    items = query.order_by(SLALog.created_at.desc()).offset(skip).limit(limit).all()
    
    return items, total

