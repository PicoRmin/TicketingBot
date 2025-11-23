from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from io import BytesIO
try:
  import openpyxl
except Exception:
  openpyxl = None
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_report_access
from app.models import User
from app.services.report_service import (
    tickets_by_status, 
    tickets_by_date, 
    tickets_overview, 
    tickets_by_branch, 
    average_response_time_hours,
    tickets_by_priority,
    tickets_by_department,
    sla_compliance_report,
    sla_by_priority
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.get("/overview")
async def overview(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
) -> Dict[str, Any]:
  return tickets_overview(db)


@router.get("/by-status")
async def report_by_status(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
) -> Dict[str, int]:
  return tickets_by_status(db)


@router.get("/by-date")
async def report_by_date(
  request: Request,
  date_from: Optional[date] = Query(None),
  date_to: Optional[date] = Query(None),
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
) -> List[Dict[str, Any]]:
  return tickets_by_date(db, date_from, date_to)


@router.get("/by-branch")
async def report_by_branch(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  return tickets_by_branch(db)


@router.get("/response-time")
async def report_response_time(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  avg_hours = average_response_time_hours(db)
  return {"average_response_time_hours": avg_hours}


@router.get("/by-priority")
async def report_by_priority(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
) -> Dict[str, int]:
  """Report tickets by priority"""
  return tickets_by_priority(db)


@router.get("/by-department")
async def report_by_department(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  """Report tickets by department"""
  return tickets_by_department(db)


@router.get("/sla-compliance")
async def report_sla_compliance(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  """SLA compliance report"""
  return sla_compliance_report(db)


@router.get("/sla-by-priority")
async def report_sla_by_priority(
  request: Request,
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  """SLA compliance report by priority"""
  return sla_by_priority(db)


@router.get("/export", response_class=PlainTextResponse)
async def export_csv(
  request: Request,
  kind: str = Query(..., description="نوع گزارش: overview|by-status|by-date|by-branch|by-priority|by-department|sla-compliance"),
  date_from: Optional[date] = Query(None),
  date_to: Optional[date] = Query(None),
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  # very basic CSV export (UTF-8)
  if kind == "overview":
    data = tickets_overview(db)
    header = "metric,value"
    rows = [f"{k},{v}" for k, v in data.items()]
    return "\n".join([header, *rows])
  if kind == "by-status":
    data = tickets_by_status(db)
    header = "status,count"
    rows = [f"{k},{v}" for k, v in data.items()]
    return "\n".join([header, *rows])
  if kind == "by-date":
    data = tickets_by_date(db, date_from, date_to)
    header = "date,count"
    rows = [f"{row['date']},{row['count']}" for row in data]
    return "\n".join([header, *rows])
  if kind == "by-branch":
    data = tickets_by_branch(db)
    header = "branch_id,branch_name,branch_code,count"
    rows = [f"{row['branch_id']},{row['branch_name']},{row['branch_code']},{row['count']}" for row in data]
    return "\n".join([header, *rows])
  if kind == "by-priority":
    data = tickets_by_priority(db)
    header = "priority,count"
    rows = [f"{k},{v}" for k, v in data.items()]
    return "\n".join([header, *rows])
  if kind == "by-department":
    data = tickets_by_department(db)
    header = "department_id,department_name,department_code,count"
    rows = [f"{row['department_id']},{row['department_name']},{row['department_code']},{row['count']}" for row in data]
    return "\n".join([header, *rows])
  if kind == "sla-compliance":
    data = sla_compliance_report(db)
    header = "metric,value"
    rows = [f"{k},{v}" for k, v in data.items()]
    return "\n".join([header, *rows])
  raise HTTPException(status_code=400, detail="Invalid kind")


@router.get("/export.xlsx")
async def export_xlsx(
  request: Request,
  kind: str = Query(..., description="overview|by-status|by-date|by-branch|by-priority|by-department|sla-compliance"),
  date_from: Optional[date] = Query(None),
  date_to: Optional[date] = Query(None),
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  if openpyxl is None:
    raise HTTPException(status_code=500, detail="openpyxl is not installed")

  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = kind

  if kind == "overview":
    data = tickets_overview(db)
    ws.append(["metric", "value"])
    for k, v in data.items():
      ws.append([k, v])
  elif kind == "by-status":
    data = tickets_by_status(db)
    ws.append(["status", "count"])
    for k, v in data.items():
      ws.append([k, v])
  elif kind == "by-date":
    data = tickets_by_date(db, date_from, date_to)
    ws.append(["date", "count"])
    for row in data:
      ws.append([row["date"], row["count"]])
  elif kind == "by-branch":
    data = tickets_by_branch(db)
    ws.append(["branch_id", "branch_name", "branch_code", "count"])
    for row in data:
      ws.append([row["branch_id"], row["branch_name"], row["branch_code"], row["count"]])
  elif kind == "by-priority":
    data = tickets_by_priority(db)
    ws.append(["priority", "count"])
    for k, v in data.items():
      ws.append([k, v])
  elif kind == "by-department":
    data = tickets_by_department(db)
    ws.append(["department_id", "department_name", "department_code", "count"])
    for row in data:
      ws.append([row["department_id"], row["department_name"], row["department_code"], row["count"]])
  elif kind == "sla-compliance":
    data = sla_compliance_report(db)
    ws.append(["metric", "value"])
    for k, v in data.items():
      ws.append([k, v])
  else:
    raise HTTPException(status_code=400, detail="Invalid kind")

  bio = BytesIO()
  wb.save(bio)
  bio.seek(0)
  return StreamingResponse(
    bio,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f'attachment; filename="report_{kind}.xlsx"'}
  )

