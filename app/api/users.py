"""User management API"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.database import get_db
from app.i18n.fastapi_utils import resolve_lang
from app.i18n.translator import translate
from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import (
    UserServiceError,
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)

router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def list_users_endpoint(
    request: Request,
    role: Optional[UserRole] = Query(None),
    branch_id: Optional[int] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lang = resolve_lang(request, current_user)

    # Branch admins can only view their own branch
    if current_user.role == UserRole.BRANCH_ADMIN:
        if current_user.branch_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=translate("common.forbidden", lang),
            )
        branch_id = current_user.branch_id
        include_inactive = bool(include_inactive)
    elif current_user.role not in (
        UserRole.ADMIN,
        UserRole.CENTRAL_ADMIN,
        UserRole.REPORT_MANAGER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translate("common.forbidden", lang),
        )

    users, _ = list_users(
        db,
        role=role,
        branch_id=branch_id,
        include_inactive=include_inactive,
    )
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    request: Request,
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN)),
):
    lang = resolve_lang(request, current_user)
    try:
        user = create_user(db, data)
        return user
    except UserServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate(f"users.{exc.message}", lang),
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    request: Request,
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRAL_ADMIN)),
):
    lang = resolve_lang(request, current_user)
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("users.not_found", lang),
        )
    try:
        updated = update_user(db, user, data)
        return updated
    except UserServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate(f"users.{exc.message}", lang),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.CENTRAL_ADMIN)),
):
    lang = resolve_lang(request, current_user)
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translate("users.not_found", lang),
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("users.cannot_delete_self", lang),
        )
    delete_user(db, user)
    return None
