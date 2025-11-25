from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, text
from app.models import Ticket, Branch, Department, SLALog, SLARule
from app.core.enums import TicketStatus, TicketCategory, TicketPriority


def tickets_by_status(db: Session) -> Dict[str, int]:
  rows = (
    db.query(Ticket.status, func.count(Ticket.id))
    .group_by(Ticket.status)
    .all()
  )
  return {status.value: count for status, count in rows}


def tickets_by_date(
  db: Session,
  date_from: Optional[date] = None,
  date_to: Optional[date] = None,
) -> List[Dict[str, int]]:
  # Use func.date() for SQLite compatibility instead of cast()
  q = db.query(func.date(Ticket.created_at).label("d"), func.count(Ticket.id))
  if date_from:
    q = q.filter(Ticket.created_at >= datetime.combine(date_from, datetime.min.time()))
  if date_to:
    q = q.filter(Ticket.created_at <= datetime.combine(date_to, datetime.max.time()))
  rows = q.group_by("d").order_by("d").all()
  # Handle both string and date objects from SQLite
  result = []
  for row in rows:
    d, c = row
    # Convert date to string if needed
    if isinstance(d, str):
      date_str = d
    elif isinstance(d, date):
      date_str = d.isoformat()
    else:
      date_str = str(d)
    result.append({"date": date_str, "count": c})
  return result


def tickets_overview(db: Session) -> Dict[str, int]:
  total = db.query(func.count(Ticket.id)).scalar() or 0
  by_status = tickets_by_status(db)
  return {"total": total, **by_status}


def tickets_by_branch(db: Session) -> List[Dict[str, any]]:
  rows = (
    db.query(Ticket.branch_id, Branch.name, Branch.code, func.count(Ticket.id))
    .join(Branch, Branch.id == Ticket.branch_id)
    .group_by(Ticket.branch_id, Branch.name, Branch.code)
    .all()
  )
  result = [{"branch_id": bid, "branch_name": name, "branch_code": code, "count": cnt} for bid, name, code, cnt in rows]
  # Also count tickets without branch
  no_branch_count = db.query(func.count(Ticket.id)).filter(Ticket.branch_id.is_(None)).scalar() or 0
  if no_branch_count > 0:
    result.append({"branch_id": None, "branch_name": "بدون شعبه", "branch_code": "NONE", "count": no_branch_count})
  return result


def average_response_time_hours(db: Session) -> Optional[float]:
  # response time: created_at -> resolved_at
  rows = (
    db.query(func.avg(func.strftime("%s", Ticket.resolved_at) - func.strftime("%s", Ticket.created_at)))
    .filter(Ticket.resolved_at.isnot(None))
    .all()
  )
  seconds = rows[0][0] if rows and rows[0][0] is not None else None
  if seconds is None:
    return None
  return float(seconds) / 3600.0


def tickets_by_priority(db: Session) -> Dict[str, int]:
  """Report tickets by priority"""
  # بعضی دیتابیس‌ها مقدار enum را به صورت نام (MEDIUM) نگه می‌دارند، برخی به صورت مقدار (medium)
  result: Dict[str, int] = {p.value: 0 for p in TicketPriority}
  query = text("SELECT priority, COUNT(id) AS cnt FROM tickets GROUP BY priority")
  rows = db.execute(query).fetchall()
  for priority_value, count in rows:
    normalized = str(priority_value or "").lower()
    if normalized in result:
      result[normalized] = count
    else:
      # fallback برای حالت‌های غیرمنتظره
      result[priority_value] = count
  return result


def tickets_by_department(db: Session) -> List[Dict[str, any]]:
  """Report tickets by department"""
  rows = (
    db.query(Ticket.department_id, Department.name, Department.code, func.count(Ticket.id))
    .join(Department, Department.id == Ticket.department_id)
    .group_by(Ticket.department_id, Department.name, Department.code)
    .all()
  )
  result = [{"department_id": did, "department_name": name, "department_code": code, "count": cnt} 
            for did, name, code, cnt in rows]
  # Also count tickets without department
  no_dept_count = db.query(func.count(Ticket.id)).filter(Ticket.department_id.is_(None)).scalar() or 0
  if no_dept_count > 0:
    result.append({"department_id": None, "department_name": "بدون دپارتمان", "department_code": "NONE", "count": no_dept_count})
  return result


def sla_compliance_report(db: Session) -> Dict[str, any]:
  """SLA compliance report"""
  total_logs = db.query(func.count(SLALog.id)).scalar() or 0
  
  if total_logs == 0:
    return {
      "total_tickets_with_sla": 0,
      "response_on_time": 0,
      "response_warning": 0,
      "response_breached": 0,
      "resolution_on_time": 0,
      "resolution_warning": 0,
      "resolution_breached": 0,
      "escalated_count": 0,
      "response_compliance_rate": 0.0,
      "resolution_compliance_rate": 0.0
    }
  
  # Response status counts
  response_on_time = db.query(func.count(SLALog.id)).filter(SLALog.response_status == "on_time").scalar() or 0
  response_warning = db.query(func.count(SLALog.id)).filter(SLALog.response_status == "warning").scalar() or 0
  response_breached = db.query(func.count(SLALog.id)).filter(SLALog.response_status == "breached").scalar() or 0
  
  # Resolution status counts
  resolution_on_time = db.query(func.count(SLALog.id)).filter(SLALog.resolution_status == "on_time").scalar() or 0
  resolution_warning = db.query(func.count(SLALog.id)).filter(SLALog.resolution_status == "warning").scalar() or 0
  resolution_breached = db.query(func.count(SLALog.id)).filter(SLALog.resolution_status == "breached").scalar() or 0
  
  # Escalated count
  escalated_count = db.query(func.count(SLALog.id)).filter(SLALog.escalated == True).scalar() or 0
  
  # Calculate compliance rates
  response_completed = response_on_time + response_breached
  resolution_completed = resolution_on_time + resolution_breached
  
  response_compliance_rate = (response_on_time / response_completed * 100) if response_completed > 0 else 0.0
  resolution_compliance_rate = (resolution_on_time / resolution_completed * 100) if resolution_completed > 0 else 0.0
  
  return {
    "total_tickets_with_sla": total_logs,
    "response_on_time": response_on_time,
    "response_warning": response_warning,
    "response_breached": response_breached,
    "resolution_on_time": resolution_on_time,
    "resolution_warning": resolution_warning,
    "resolution_breached": resolution_breached,
    "escalated_count": escalated_count,
    "response_compliance_rate": round(response_compliance_rate, 2),
    "resolution_compliance_rate": round(resolution_compliance_rate, 2)
  }


def sla_by_priority(db: Session) -> List[Dict[str, any]]:
  """SLA compliance report by priority"""
  result = []
  
  for priority in TicketPriority:
    # Get SLA rule for this priority
    sla_rule = db.query(SLARule).filter(
      SLARule.priority == priority,
      SLARule.is_active == True
    ).first()
    
    if not sla_rule:
      continue
    
    # Get tickets with this priority and their SLA logs
    tickets_with_sla = (
      db.query(Ticket, SLALog)
      .join(SLALog, SLALog.ticket_id == Ticket.id)
      .filter(
        Ticket.priority == priority,
        SLALog.sla_rule_id == sla_rule.id
      )
      .all()
    )
    
    total = len(tickets_with_sla)
    if total == 0:
      continue
    
    response_on_time = sum(1 for t, log in tickets_with_sla if log.response_status == "on_time")
    response_breached = sum(1 for t, log in tickets_with_sla if log.response_status == "breached")
    resolution_on_time = sum(1 for t, log in tickets_with_sla if log.resolution_status == "on_time")
    resolution_breached = sum(1 for t, log in tickets_with_sla if log.resolution_status == "breached")
    
    response_completed = response_on_time + response_breached
    resolution_completed = resolution_on_time + resolution_breached
    
    result.append({
      "priority": priority.value,
      "total_tickets": total,
      "response_on_time": response_on_time,
      "response_breached": response_breached,
      "resolution_on_time": resolution_on_time,
      "resolution_breached": resolution_breached,
      "response_compliance_rate": round((response_on_time / response_completed * 100) if response_completed > 0 else 0.0, 2),
      "resolution_compliance_rate": round((resolution_on_time / resolution_completed * 100) if resolution_completed > 0 else 0.0, 2)
    })
  
  return result

