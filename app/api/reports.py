from datetime import date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import PlainTextResponse, StreamingResponse, Response
from io import BytesIO
try:
  import openpyxl
except Exception:
  openpyxl = None
try:
  from reportlab.lib.pagesizes import A4
  from reportlab.lib import colors
  from reportlab.lib.units import cm
  from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
  from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
  from reportlab.pdfbase import pdfmetrics
  from reportlab.pdfbase.ttfonts import TTFont
  REPORTLAB_AVAILABLE = True
except Exception:
  REPORTLAB_AVAILABLE = False
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


@router.get("/export-pdf")
async def export_pdf(
  request: Request,
  date_from: Optional[date] = Query(None),
  date_to: Optional[date] = Query(None),
  branch_id: Optional[int] = Query(None),
  department_id: Optional[int] = Query(None),
  priority: Optional[str] = Query(None),
  db: Session = Depends(get_db),
  _current_user: User = Depends(require_report_access)
):
  """Export comprehensive dashboard report as PDF"""
  if not REPORTLAB_AVAILABLE:
    raise HTTPException(status_code=500, detail="ReportLab is not installed")
  
  # Collect all report data
  overview_data = tickets_overview(db)
  status_data = tickets_by_status(db)
  date_data = tickets_by_date(db, date_from, date_to)
  branch_data = tickets_by_branch(db)
  priority_data = tickets_by_priority(db)
  department_data = tickets_by_department(db)
  sla_data = sla_compliance_report(db)
  response_time = average_response_time_hours(db)
  
  # Create PDF
  bio = BytesIO()
  doc = SimpleDocTemplate(bio, pagesize=A4)
  story = []
  styles = getSampleStyleSheet()
  
  # Title
  title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=30,
    alignment=1  # Center
  )
  story.append(Paragraph("گزارش جامع داشبورد سیستم تیکتینگ", title_style))
  story.append(Spacer(1, 0.5*cm))
  
  # Overview Section
  story.append(Paragraph("خلاصه کلی", styles['Heading2']))
  overview_table_data = [
    ['معیار', 'مقدار'],
    ['مجموع تیکت‌ها', str(overview_data.get('total', 0))],
    ['در انتظار', str(overview_data.get('pending', 0))],
    ['در حال انجام', str(overview_data.get('in_progress', 0))],
    ['حل شده', str(overview_data.get('resolved', 0))],
    ['بسته شده', str(overview_data.get('closed', 0))],
  ]
  if response_time:
    overview_table_data.append(['میانگین زمان پاسخ (ساعت)', f"{response_time:.2f}"])
  
  overview_table = Table(overview_table_data, colWidths=[8*cm, 8*cm])
  overview_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ]))
  story.append(overview_table)
  story.append(Spacer(1, 0.5*cm))
  
  # Status Section
  story.append(Paragraph("تیکت‌ها بر اساس وضعیت", styles['Heading2']))
  status_table_data = [['وضعیت', 'تعداد']]
  status_map = {
    'pending': 'در انتظار',
    'in_progress': 'در حال انجام',
    'resolved': 'حل شده',
    'closed': 'بسته شده'
  }
  for status, count in status_data.items():
    status_table_data.append([status_map.get(status, status), str(count)])
  
  status_table = Table(status_table_data, colWidths=[8*cm, 8*cm])
  status_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ]))
  story.append(status_table)
  story.append(Spacer(1, 0.5*cm))
  
  # Priority Section
  story.append(Paragraph("تیکت‌ها بر اساس اولویت", styles['Heading2']))
  priority_table_data = [['اولویت', 'تعداد']]
  priority_map = {
    'critical': 'بحرانی',
    'high': 'بالا',
    'medium': 'متوسط',
    'low': 'پایین'
  }
  for pri, count in priority_data.items():
    priority_table_data.append([priority_map.get(pri, pri), str(count)])
  
  priority_table = Table(priority_table_data, colWidths=[8*cm, 8*cm])
  priority_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
  ]))
  story.append(priority_table)
  story.append(Spacer(1, 0.5*cm))
  
  # SLA Section
  if sla_data and sla_data.get('total_tickets_with_sla', 0) > 0:
    story.append(Paragraph("گزارش رعایت SLA", styles['Heading2']))
    sla_table_data = [
      ['معیار', 'مقدار'],
      ['مجموع تیکت‌های دارای SLA', str(sla_data.get('total_tickets_with_sla', 0))],
      ['پاسخ در مهلت', str(sla_data.get('response_on_time', 0))],
      ['پاسخ هشدار', str(sla_data.get('response_warning', 0))],
      ['پاسخ نقض شده', str(sla_data.get('response_breached', 0))],
      ['نرخ رعایت پاسخ (%)', f"{sla_data.get('response_compliance_rate', 0):.1f}"],
      ['حل در مهلت', str(sla_data.get('resolution_on_time', 0))],
      ['حل هشدار', str(sla_data.get('resolution_warning', 0))],
      ['حل نقض شده', str(sla_data.get('resolution_breached', 0))],
      ['نرخ رعایت حل (%)', f"{sla_data.get('resolution_compliance_rate', 0):.1f}"],
    ]
    
    sla_table = Table(sla_table_data, colWidths=[8*cm, 8*cm])
    sla_table.setStyle(TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('FONTSIZE', (0, 0), (-1, 0), 12),
      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
      ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
      ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(sla_table)
    story.append(Spacer(1, 0.5*cm))
  
  # Footer
  from datetime import datetime
  story.append(Spacer(1, 1*cm))
  footer_style = ParagraphStyle(
    'Footer',
    parent=styles['Normal'],
    fontSize=8,
    textColor=colors.grey,
    alignment=1
  )
  story.append(Paragraph(f"تاریخ تولید: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
  
  # Build PDF
  doc.build(story)
  bio.seek(0)
  
  return StreamingResponse(
    bio,
    media_type="application/pdf",
    headers={"Content-Disposition": f'attachment; filename="dashboard-report-{datetime.now().strftime("%Y%m%d")}.pdf"'}
  )

