from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Branch, User
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse
from app.api.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.services.branch_service import (
  create_branch,
  get_branch,
  get_branch_by_code,
  list_branches,
  update_branch as svc_update_branch,
)
from app.i18n.fastapi_utils import resolve_lang
from app.i18n.translator import translate

router = APIRouter()


@router.get("", response_model=List[BranchResponse])
async def get_branches(
  request: Request,
  is_active: Optional[bool] = Query(None),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_active_user)
):
  branches, _ = list_branches(db, is_active=is_active)
  return branches


@router.post("", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def add_branch(
  request: Request,
  data: BranchCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN))
):
  if get_branch_by_code(db, data.code):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=translate("validation.invalid_credentials", resolve_lang(request, current_user))
    )
  branch = create_branch(db, data)
  return branch


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch_by_id(
  request: Request,
  branch_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_active_user)
):
  branch = get_branch(db, branch_id)
  if not branch:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
  return branch


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
  request: Request,
  branch_id: int,
  data: BranchUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN))
):
  branch = get_branch(db, branch_id)
  if not branch:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
  return svc_update_branch(db, branch, data)

