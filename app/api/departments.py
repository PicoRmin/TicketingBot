"""
Departments API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Department, User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from app.api.deps import get_current_active_user, require_admin
from app.services.department_service import (
    create_department,
    get_department,
    get_department_by_code,
    list_departments,
    update_department,
    delete_department,
)
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_new_department(
    request: Request,
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new department (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    # Check if code already exists
    existing = get_department_by_code(db, department_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("departments.code_exists", lang) or f"کد دپارتمان '{department_data.code}' قبلاً استفاده شده است."
        )
    
    # Check if name already exists
    existing_name = db.query(Department).filter(Department.name == department_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("departments.name_exists", lang) or f"نام دپارتمان '{department_data.name}' قبلاً استفاده شده است."
        )
    
    department = create_department(db, department_data)
    return department


@router.get("", response_model=list[DepartmentResponse])
async def get_departments(
    request: Request,
    page: int = Query(1, ge=1, description="شماره صفحه"),
    page_size: int = Query(50, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    is_active: Optional[bool] = Query(None, description="فیلتر بر اساس وضعیت"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of departments"""
    skip = (page - 1) * page_size
    departments, total = list_departments(db, skip=skip, limit=page_size, is_active=is_active)
    return departments


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department_by_id(
    request: Request,
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get department by ID"""
    department = get_department(db, department_id)
    if not department:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("departments.not_found", lang) or "دپارتمان یافت نشد."
        )
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department_by_id(
    request: Request,
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update department (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("departments.not_found", lang) or "دپارتمان یافت نشد."
        )
    
    # Check if new code already exists
    if department_data.code and department_data.code != department.code:
        existing = get_department_by_code(db, department_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate("departments.code_exists", lang) or f"کد دپارتمان '{department_data.code}' قبلاً استفاده شده است."
            )
    
    # Check if new name already exists
    if department_data.name and department_data.name != department.name:
        existing_name = db.query(Department).filter(Department.name == department_data.name).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translate("departments.name_exists", lang) or f"نام دپارتمان '{department_data.name}' قبلاً استفاده شده است."
            )
    
    updated = update_department(db, department, department_data)
    return updated


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_by_id(
    request: Request,
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete department (Admin only)"""
    lang = resolve_lang(request, current_user)
    
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("departments.not_found", lang) or "دپارتمان یافت نشد."
        )
    
    # Check if department has users or tickets
    if department.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("departments.has_users", lang) or "نمی‌توان دپارتمانی که کاربر دارد را حذف کرد."
        )
    
    if department.tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("departments.has_tickets", lang) or "نمی‌توان دپارتمانی که تیکت دارد را حذف کرد."
        )
    
    success = delete_department(db, department)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("common.error", lang)
        )

