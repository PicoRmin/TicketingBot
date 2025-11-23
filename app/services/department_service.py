"""
Department service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def create_department(db: Session, department_data: DepartmentCreate) -> Department:
    """Create new department"""
    department = Department(**department_data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get department by ID"""
    return db.query(Department).filter(Department.id == department_id).first()


def get_department_by_code(db: Session, code: str) -> Optional[Department]:
    """Get department by code"""
    return db.query(Department).filter(Department.code == code).first()


def list_departments(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None
) -> tuple[List[Department], int]:
    """List departments with pagination"""
    query = db.query(Department)
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    total = query.count()
    items = query.offset(skip).limit(limit).order_by(Department.name).all()
    return items, total


def update_department(
    db: Session,
    department: Department,
    department_data: DepartmentUpdate
) -> Department:
    """Update department"""
    update_data = department_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return department


def delete_department(db: Session, department: Department) -> bool:
    """Delete department"""
    try:
        db.delete(department)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

