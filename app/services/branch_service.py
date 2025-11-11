from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Branch
from app.schemas.branch import BranchCreate, BranchUpdate


def create_branch(db: Session, data: BranchCreate) -> Branch:
  branch = Branch(
    name=data.name,
    name_en=data.name_en,
    code=data.code,
    address=data.address,
    phone=data.phone,
    is_active=data.is_active,
  )
  db.add(branch)
  db.commit()
  db.refresh(branch)
  return branch


def get_branch(db: Session, branch_id: int) -> Optional[Branch]:
  return db.query(Branch).filter(Branch.id == branch_id).first()


def get_branch_by_code(db: Session, code: str) -> Optional[Branch]:
  return db.query(Branch).filter(Branch.code == code).first()


def list_branches(db: Session, skip: int = 0, limit: int = 50, is_active: Optional[bool] = None) -> Tuple[List[Branch], int]:
  query = db.query(Branch)
  if is_active is not None:
    query = query.filter(Branch.is_active == is_active)
  total = query.count()
  items = query.offset(skip).limit(limit).all()
  return items, total


def update_branch(db: Session, branch: Branch, data: BranchUpdate) -> Branch:
  for field, value in data.model_dump(exclude_unset=True).items():
    setattr(branch, field, value)
  db.add(branch)
  db.commit()
  db.refresh(branch)
  return branch

