"""Refresh token management service"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models import RefreshToken, User


def _hash_token(token: str) -> str:
    secret = settings.REFRESH_TOKEN_SECRET or ""
    return hashlib.sha256(f"{token}{secret}".encode("utf-8")).hexdigest()


def issue_refresh_token(
    db: Session,
    user: User,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[str, RefreshToken]:
    """Create and persist a new refresh token for user, returning plain token."""
    plain_token = secrets.token_urlsafe(48)
    token_hash = _hash_token(plain_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=ip_address,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return plain_token, record


def verify_refresh_token(db: Session, refresh_token: str) -> Optional[RefreshToken]:
    """Validate refresh token and return record if valid."""
    token_hash = _hash_token(refresh_token)
    record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
        )
        .first()
    )
    if not record:
        return None
    if record.expires_at < datetime.utcnow():
        return None
    db.refresh(record)
    return record


def revoke_refresh_token(db: Session, record: RefreshToken) -> None:
    """Mark refresh token as revoked."""
    if record.revoked:
        return
    record.revoked = True
    record.revoked_at = datetime.utcnow()
    db.add(record)
    db.commit()


def rotate_refresh_token(
    db: Session,
    record: RefreshToken,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[str, RefreshToken]:
    """Revoke current token and issue a new one."""
    revoke_refresh_token(db, record)
    return issue_refresh_token(db, record.user, user_agent=user_agent, ip_address=ip_address)
