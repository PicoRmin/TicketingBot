"""
Automation service for auto-assignment and other automation
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.models import AutomationRule, Ticket, User, Department
from app.core.enums import TicketPriority, TicketCategory, UserRole
from app.schemas.automation_rule import AutomationRuleCreate, AutomationRuleUpdate
import logging

logger = logging.getLogger(__name__)


def check_conditions(ticket: Ticket, conditions: dict) -> bool:
    """
    Check if ticket matches automation rule conditions
    
    Args:
        ticket: Ticket to check
        conditions: Conditions dictionary
        
    Returns:
        bool: True if conditions match
    """
    if not conditions:
        return True
    
    # Check priority
    if "priority" in conditions:
        if ticket.priority.value != conditions["priority"]:
            return False
    
    # Check category
    if "category" in conditions:
        if ticket.category.value != conditions["category"]:
            return False
    
    # Check department
    if "department_id" in conditions:
        if ticket.department_id != conditions["department_id"]:
            return False
    
    # Check branch
    if "branch_id" in conditions:
        if ticket.branch_id != conditions["branch_id"]:
            return False
    
    # Check status
    if "status" in conditions:
        if ticket.status.value != conditions["status"]:
            return False
    
    return True


def auto_assign_ticket(db: Session, ticket: Ticket) -> Optional[User]:
    """
    Auto-assign ticket based on automation rules
    
    Args:
        db: Database session
        ticket: Ticket to assign
        
    Returns:
        User or None if no assignment made
    """
    # Get active auto-assign rules ordered by priority
    rules = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.rule_type == "auto_assign",
            AutomationRule.is_active == True
        )
        .order_by(AutomationRule.priority.asc())
        .all()
    )
    
    for rule in rules:
        # Check conditions
        if not check_conditions(ticket, rule.conditions):
            continue
        
        actions = rule.actions or {}
        
        # Assign to specific user
        if "assign_to_user_id" in actions:
            user_id = actions["assign_to_user_id"]
            user = db.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            if user:
                ticket.assigned_to_id = user.id
                db.commit()
                logger.info(f"Auto-assigned ticket {ticket.id} to user {user.username} via rule {rule.name}")
                return user
        
        # Assign to department with round-robin
        elif "assign_to_department_id" in actions:
            department_id = actions["assign_to_department_id"]
            use_round_robin = actions.get("round_robin", False)
            
            department = db.query(Department).filter(Department.id == department_id).first()
            if not department:
                continue
            
            # Get users in department
            users = (
                db.query(User)
                .filter(
                    User.department_id == department_id,
                    User.is_active == True,
                    User.role.in_([UserRole.IT_SPECIALIST, UserRole.ADMIN, UserRole.BRANCH_ADMIN])
                )
                .all()
            )
            
            if not users:
                continue
            
            if use_round_robin:
                # Round-robin: assign to user with least assigned tickets
                from sqlalchemy import func
                user_counts = (
                    db.query(Ticket.assigned_to_id, func.count(Ticket.id).label('count'))
                    .filter(
                        Ticket.assigned_to_id.in_([u.id for u in users]),
                        Ticket.status.in_(["pending", "in_progress"])
                    )
                    .group_by(Ticket.assigned_to_id)
                    .all()
                )
                
                # Create count map
                count_map = {uid: cnt for uid, cnt in user_counts}
                
                # Find user with minimum count
                selected_user = min(users, key=lambda u: count_map.get(u.id, 0))
            else:
                # Assign to first available user
                selected_user = users[0]
            
            ticket.assigned_to_id = selected_user.id
            db.commit()
            logger.info(f"Auto-assigned ticket {ticket.id} to user {selected_user.username} via rule {rule.name}")
            return selected_user
        
        # Assign to role
        elif "assign_to_role" in actions:
            role = actions["assign_to_role"]
            users = (
                db.query(User)
                .filter(
                    User.role == role,
                    User.is_active == True
                )
                .all()
            )
            
            if users:
                # Round-robin if specified
                if actions.get("round_robin", False):
                    from sqlalchemy import func
                    user_counts = (
                        db.query(Ticket.assigned_to_id, func.count(Ticket.id).label('count'))
                        .filter(
                            Ticket.assigned_to_id.in_([u.id for u in users]),
                            Ticket.status.in_(["pending", "in_progress"])
                        )
                        .group_by(Ticket.assigned_to_id)
                        .all()
                    )
                    count_map = {uid: cnt for uid, cnt in user_counts}
                    selected_user = min(users, key=lambda u: count_map.get(u.id, 0))
                else:
                    selected_user = users[0]
                
                ticket.assigned_to_id = selected_user.id
                db.commit()
                logger.info(f"Auto-assigned ticket {ticket.id} to user {selected_user.username} via rule {rule.name}")
                return selected_user
    
    return None


def create_automation_rule(db: Session, rule_data: AutomationRuleCreate) -> AutomationRule:
    """Create new automation rule"""
    rule = AutomationRule(**rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_automation_rule(db: Session, rule_id: int) -> Optional[AutomationRule]:
    """Get automation rule by ID"""
    return db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()


def list_automation_rules(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    rule_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[AutomationRule], int]:
    """List automation rules with pagination"""
    query = db.query(AutomationRule)
    if rule_type:
        query = query.filter(AutomationRule.rule_type == rule_type)
    if is_active is not None:
        query = query.filter(AutomationRule.is_active == is_active)
    total = query.count()
    items = query.order_by(AutomationRule.priority.asc(), AutomationRule.name).offset(skip).limit(limit).all()
    return items, total


def update_automation_rule(
    db: Session,
    rule: AutomationRule,
    rule_data: AutomationRuleUpdate
) -> AutomationRule:
    """Update automation rule"""
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


def delete_automation_rule(db: Session, rule: AutomationRule) -> bool:
    """Delete automation rule"""
    try:
        db.delete(rule)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def auto_close_tickets(db: Session) -> int:
    """
    Auto-close tickets based on automation rules
    
    Args:
        db: Database session
        
    Returns:
        int: Number of tickets closed
    """
    from datetime import datetime, timedelta
    from app.core.enums import TicketStatus
    
    closed_count = 0
    
    # Get active auto-close rules
    rules = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.rule_type == "auto_close",
            AutomationRule.is_active == True
        )
        .order_by(AutomationRule.priority.asc())
        .all()
    )
    
    for rule in rules:
        actions = rule.actions or {}
        close_after_hours = actions.get("close_after_hours")
        only_if_resolved = actions.get("only_if_resolved", False)
        
        if not close_after_hours:
            continue
        
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=close_after_hours)
        
        # Build query for tickets to close
        query = db.query(Ticket).filter(
            Ticket.created_at <= cutoff_time,
            Ticket.status != TicketStatus.CLOSED
        )
        
        # Apply conditions
        if rule.conditions:
            if "priority" in rule.conditions:
                from app.core.enums import TicketPriority
                query = query.filter(Ticket.priority == TicketPriority(rule.conditions["priority"]))
            if "category" in rule.conditions:
                from app.core.enums import TicketCategory
                query = query.filter(Ticket.category == TicketCategory(rule.conditions["category"]))
            if "department_id" in rule.conditions:
                query = query.filter(Ticket.department_id == rule.conditions["department_id"])
            if "branch_id" in rule.conditions:
                query = query.filter(Ticket.branch_id == rule.conditions["branch_id"])
        
        # If only_if_resolved, only close resolved tickets
        if only_if_resolved:
            query = query.filter(Ticket.status == TicketStatus.RESOLVED)
        
        tickets_to_close = query.all()
        
        for ticket in tickets_to_close:
            try:
                from app.services.ticket_service import update_ticket_status
                from app.services.ticket_history_service import create_ticket_history
                from app.schemas.ticket_history import TicketHistoryCreate
                
                previous_status = ticket.status
                update_ticket_status(db, ticket, TicketStatus.CLOSED)
                
                # Create history entry
                create_ticket_history(
                    db,
                    TicketHistoryCreate(
                        ticket_id=ticket.id,
                        status=TicketStatus.CLOSED,
                        changed_by_id=None,  # System action
                        comment=f"بسته شدن خودکار توسط قانون '{rule.name}'",
                    ),
                )
                
                closed_count += 1
                logger.info(f"Auto-closed ticket {ticket.ticket_number} via rule {rule.name}")
            except Exception as e:
                logger.error(f"Failed to auto-close ticket {ticket.id}: {e}")
                db.rollback()
                continue
    
    return closed_count


def auto_notify_tickets(db: Session) -> int:
    """
    Auto-notify users based on automation rules
    
    Args:
        db: Database session
        
    Returns:
        int: Number of notifications sent
    """
    from app.core.enums import TicketStatus
    
    notified_count = 0
    
    # Get active auto-notify rules
    rules = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.rule_type == "auto_notify",
            AutomationRule.is_active == True
        )
        .order_by(AutomationRule.priority.asc())
        .all()
    )
    
    for rule in rules:
        actions = rule.actions or {}
        notify_users = actions.get("notify_users", [])
        notify_roles = actions.get("notify_roles", [])
        message = actions.get("message", "")
        
        if not notify_users and not notify_roles:
            continue
        
        # Build query for tickets to notify about
        query = db.query(Ticket)
        
        # Apply conditions
        if rule.conditions:
            if "priority" in rule.conditions:
                from app.core.enums import TicketPriority
                query = query.filter(Ticket.priority == TicketPriority(rule.conditions["priority"]))
            if "category" in rule.conditions:
                from app.core.enums import TicketCategory
                query = query.filter(Ticket.category == TicketCategory(rule.conditions["category"]))
            if "department_id" in rule.conditions:
                query = query.filter(Ticket.department_id == rule.conditions["department_id"])
            if "branch_id" in rule.conditions:
                query = query.filter(Ticket.branch_id == rule.conditions["branch_id"])
            if "status" in rule.conditions:
                query = query.filter(Ticket.status == TicketStatus(rule.conditions["status"]))
        
        tickets = query.all()
        
        # Get users to notify
        users_to_notify = []
        if notify_users:
            users_to_notify.extend(
                db.query(User).filter(User.id.in_(notify_users), User.is_active == True).all()
            )
        if notify_roles:
            from app.core.enums import UserRole
            users_to_notify.extend(
                db.query(User).filter(
                    User.role.in_([UserRole(role) for role in notify_roles]),
                    User.is_active == True
                ).all()
            )
        
        # Remove duplicates
        users_to_notify = list(set(users_to_notify))
        
        # Send notifications (for now, just log - can be extended to email/telegram)
        for ticket in tickets:
            for user in users_to_notify:
                try:
                    # Here you can integrate with notification service
                    # For now, we'll just log it
                    notification_text = message or f"تیکت {ticket.ticket_number} نیاز به توجه دارد."
                    logger.info(f"Auto-notify: Sending notification to user {user.username} about ticket {ticket.ticket_number}: {notification_text}")
                    notified_count += 1
                except Exception as e:
                    logger.error(f"Failed to send notification to user {user.id}: {e}")
    
    return notified_count


def process_automation_rules(db: Session) -> dict:
    """
    Process all automation rules (auto-close and auto-notify)
    
    Args:
        db: Database session
        
    Returns:
        dict: Statistics about processed rules
    """
    closed_count = auto_close_tickets(db)
    notified_count = auto_notify_tickets(db)
    
    return {
        "closed_tickets": closed_count,
        "notifications_sent": notified_count
    }

