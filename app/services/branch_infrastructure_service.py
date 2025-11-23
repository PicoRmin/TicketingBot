"""
Branch Infrastructure service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import BranchInfrastructure, Branch
from app.schemas.branch_infrastructure import BranchInfrastructureCreate, BranchInfrastructureUpdate


def create_infrastructure(
    db: Session,
    infrastructure_data: BranchInfrastructureCreate,
    created_by_id: int
) -> BranchInfrastructure:
    """Create new branch infrastructure"""
    infrastructure = BranchInfrastructure(
        **infrastructure_data.model_dump(),
        created_by_id=created_by_id
    )
    db.add(infrastructure)
    db.commit()
    db.refresh(infrastructure)
    return infrastructure


def get_infrastructure(db: Session, infrastructure_id: int) -> Optional[BranchInfrastructure]:
    """Get infrastructure by ID"""
    return db.query(BranchInfrastructure).filter(BranchInfrastructure.id == infrastructure_id).first()


def get_branch_infrastructure(
    db: Session,
    branch_id: int,
    infrastructure_type: Optional[str] = None
) -> List[BranchInfrastructure]:
    """Get all infrastructure for a branch, optionally filtered by type"""
    query = db.query(BranchInfrastructure).filter(BranchInfrastructure.branch_id == branch_id)
    if infrastructure_type:
        query = query.filter(BranchInfrastructure.infrastructure_type == infrastructure_type)
    return query.order_by(BranchInfrastructure.created_at.desc()).all()


def update_infrastructure(
    db: Session,
    infrastructure: BranchInfrastructure,
    infrastructure_data: BranchInfrastructureUpdate,
    updated_by_id: int
) -> BranchInfrastructure:
    """Update infrastructure"""
    update_data = infrastructure_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(infrastructure, field, value)
    infrastructure.updated_by_id = updated_by_id
    db.commit()
    db.refresh(infrastructure)
    return infrastructure


def delete_infrastructure(db: Session, infrastructure: BranchInfrastructure) -> bool:
    """Delete infrastructure"""
    try:
        db.delete(infrastructure)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

