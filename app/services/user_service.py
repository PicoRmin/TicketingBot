"""User service for admin management"""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.core.enums import UserRole
from app.core.security import get_password_hash
from app.models import Branch, User
from app.schemas.user import UserCreate, UserUpdate


class UserServiceError(Exception):
    """Raised for user service validation errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _ensure_branch(db: Session, branch_id: Optional[int]) -> Optional[Branch]:
    if branch_id is None:
        return None
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise UserServiceError("branch_not_found")
    return branch


def _ensure_branch_admin_unique(db: Session, branch_id: int, exclude_user_id: Optional[int] = None) -> None:
    existing = (
        db.query(User)
        .filter(
            User.role == UserRole.BRANCH_ADMIN,
            User.branch_id == branch_id,
            User.is_active.is_(True),
        )
        .first()
    )
    if existing and existing.id != exclude_user_id:
        raise UserServiceError("branch_admin_exists")


def list_users(
    db: Session,
    *,
    role: Optional[UserRole] = None,
    branch_id: Optional[int] = None,
    include_inactive: bool = False,
) -> Tuple[List[User], int]:
    query = db.query(User).options(joinedload(User.branch))
    if role:
        query = query.filter(User.role == role)
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    if not include_inactive:
        query = query.filter(User.is_active.is_(True))

    total = query.count()
    users = query.order_by(User.created_at.desc()).all()
    return users, total


def get_user(db: Session, user_id: int) -> Optional[User]:
    return (
        db.query(User)
        .options(joinedload(User.branch))
        .filter(User.id == user_id)
        .first()
    )


def create_user(db: Session, data: UserCreate) -> User:
    # Username uniqueness
    if db.query(User).filter(User.username == data.username).first():
        raise UserServiceError("username_exists")

    branch = _ensure_branch(db, data.branch_id)

    if data.role == UserRole.BRANCH_ADMIN:
        if branch is None:
            raise UserServiceError("branch_required")
        _ensure_branch_admin_unique(db, branch.id)

    user = User(
        username=data.username,
        full_name=data.full_name,
        password_hash=get_password_hash(data.password),
        role=data.role,
        language=data.language,
        branch_id=branch.id if branch else None,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(user, attribute_names=["branch"])
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    # Username is immutable (user.username)
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.language is not None:
        user.language = data.language
    if data.is_active is not None:
        user.is_active = data.is_active

    target_role = data.role or user.role

    target_branch_id = data.branch_id if data.branch_id is not None else user.branch_id
    branch = _ensure_branch(db, target_branch_id) if target_branch_id is not None else None

    if target_role == UserRole.BRANCH_ADMIN:
        if branch is None:
            raise UserServiceError("branch_required")
        _ensure_branch_admin_unique(db, branch.id, exclude_user_id=user.id)

    if data.role is not None:
        user.role = data.role
    user.branch_id = branch.id if branch else None

    if data.password:
        user.password_hash = get_password_hash(data.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(user, attribute_names=["branch"])
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
