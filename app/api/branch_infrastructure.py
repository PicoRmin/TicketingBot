"""
Branch Infrastructure API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import BranchInfrastructure, Branch, User
from app.schemas.branch_infrastructure import (
    BranchInfrastructureCreate,
    BranchInfrastructureUpdate,
    BranchInfrastructureResponse
)
from app.api.deps import get_current_active_user, require_roles, require_central_admin
from app.services.branch_infrastructure_service import (
    create_infrastructure,
    get_infrastructure,
    get_branch_infrastructure,
    update_infrastructure,
    delete_infrastructure,
)
from app.services.branch_service import get_branch
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang
from app.core.enums import UserRole

router = APIRouter()


@router.post("", response_model=BranchInfrastructureResponse, status_code=status.HTTP_201_CREATED)
async def create_branch_infrastructure(
    request: Request,
    infrastructure_data: BranchInfrastructureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN, UserRole.IT_SPECIALIST))
):
    """Create new branch infrastructure (central, admin, IT specialist)"""
    lang = resolve_lang(request, current_user)
    
    # Verify branch exists
    branch = get_branch(db, infrastructure_data.branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("branches.not_found", lang)
        )
    
    if current_user.role == UserRole.IT_SPECIALIST:
        if not current_user.branch_id or current_user.branch_id != infrastructure_data.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", resolve_lang(request, current_user))
            )
    infrastructure = create_infrastructure(db, infrastructure_data, current_user.id)
    return infrastructure


@router.get("", response_model=List[BranchInfrastructureResponse])
async def list_branch_infrastructure(
    request: Request,
    branch_id: Optional[int] = Query(None, description="فیلتر بر اساس شعبه"),
    infrastructure_type: Optional[str] = Query(None, description="فیلتر بر اساس نوع"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN, UserRole.IT_SPECIALIST))
):
    """List branch infrastructure (central/admin/IT specialist)"""
    lang = resolve_lang(request, current_user)
    if current_user.role == UserRole.IT_SPECIALIST:
        if not current_user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang)
            )
        if branch_id and branch_id != current_user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang)
            )
        branch_id = current_user.branch_id

    if branch_id:
        infrastructure_list = get_branch_infrastructure(db, branch_id, infrastructure_type)
    else:
        # Get all infrastructure
        query = db.query(BranchInfrastructure)
        if infrastructure_type:
            query = query.filter(BranchInfrastructure.infrastructure_type == infrastructure_type)
        infrastructure_list = query.order_by(BranchInfrastructure.created_at.desc()).all()
    
    return infrastructure_list


@router.get("/{infrastructure_id}", response_model=BranchInfrastructureResponse)
async def get_branch_infrastructure_by_id(
    request: Request,
    infrastructure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN, UserRole.IT_SPECIALIST))
):
    """Get infrastructure by ID (central/admin/IT specialist)"""
    infrastructure = get_infrastructure(db, infrastructure_id)
    if not infrastructure:
        lang = resolve_lang(request, current_user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("common.not_found", lang)
        )
    if current_user.role == UserRole.IT_SPECIALIST and current_user.branch_id != infrastructure.branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    return infrastructure


@router.put("/{infrastructure_id}", response_model=BranchInfrastructureResponse)
async def update_branch_infrastructure_by_id(
    request: Request,
    infrastructure_id: int,
    infrastructure_data: BranchInfrastructureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN, UserRole.ADMIN, UserRole.IT_SPECIALIST))
):
    """Update infrastructure (central/admin/IT specialist)"""
    lang = resolve_lang(request, current_user)
    
    infrastructure = get_infrastructure(db, infrastructure_id)
    if not infrastructure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("common.not_found", lang)
        )
    
    # Verify branch if branch_id is being updated
    if infrastructure_data.branch_id and infrastructure_data.branch_id != infrastructure.branch_id:
        branch = get_branch(db, infrastructure_data.branch_id)
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=translate("branches.not_found", lang)
            )
    
    if current_user.role == UserRole.IT_SPECIALIST and current_user.branch_id != infrastructure.branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", resolve_lang(request, current_user))
        )
    if infrastructure_data.branch_id and current_user.role == UserRole.IT_SPECIALIST:
        if infrastructure_data.branch_id != current_user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", resolve_lang(request, current_user))
            )
    updated = update_infrastructure(db, infrastructure, infrastructure_data, current_user.id)
    return updated


@router.delete("/{infrastructure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch_infrastructure_by_id(
    request: Request,
    infrastructure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_central_admin)
):
    """Delete infrastructure (central admin only)"""
    lang = resolve_lang(request, current_user)
    
    infrastructure = get_infrastructure(db, infrastructure_id)
    if not infrastructure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("common.not_found", lang)
        )
    
    success = delete_infrastructure(db, infrastructure)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("common.error", lang)
        )

