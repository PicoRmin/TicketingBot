from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from app.models import Ticket, Branch
from app.core.enums import TicketStatus, TicketCategory


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
  q = db.query(cast(Ticket.created_at, Date).label("d"), func.count(Ticket.id))
  if date_from:
    q = q.filter(Ticket.created_at >= datetime.combine(date_from, datetime.min.time()))
  if date_to:
    q = q.filter(Ticket.created_at <= datetime.combine(date_to, datetime.max.time()))
  rows = q.group_by("d").order_by("d").all()
  return [{"date": str(d), "count": c} for d, c in rows]


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
  return [{"branch_id": bid, "branch_name": name, "branch_code": code, "count": cnt} for bid, name, code, cnt in rows]


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

