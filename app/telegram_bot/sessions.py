"""
User session management for the Telegram bot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.core.enums import Language
from app.database import SessionLocal


@dataclass
class UserSession:
    """In-memory representation of a user session."""

    language: Language = Language.FA
    token: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    data: Dict[str, Any] = field(default_factory=dict)


_sessions: Dict[int, UserSession] = {}


def get_session(user_id: int) -> UserSession:
    """Return the session object for a given user ID."""
    session = _sessions.setdefault(user_id, UserSession())

    # Normalise language if it was set via string (e.g. from API profile)
    if isinstance(session.language, str):
        try:
            session.language = Language(session.language)
        except ValueError:
            session.language = Language.FA
    return session


def clear_session(user_id: int) -> None:
    """Remove a user session."""
    _sessions.pop(user_id, None)


def update_session_activity_in_db(telegram_user_id: int, token: Optional[str]) -> None:
    """
    Update session activity in database
    
    Args:
        telegram_user_id: Telegram user ID
        token: JWT access token
    """
    if not token:
        return
    
    try:
        from app.services.telegram_session_service import update_session_activity
        db = SessionLocal()
        try:
            update_session_activity(db, telegram_user_id, token)
        finally:
            db.close()
    except Exception:
        # Silently fail if database update fails
        pass


def set_language(user_id: int, language: Language) -> None:
    session = get_session(user_id)
    session.language = language


def get_language(user_id: int) -> Language:
    return get_session(user_id).language


def set_token(user_id: int, token: Optional[str]) -> None:
    session = get_session(user_id)
    session.token = token


def get_token(user_id: int) -> Optional[str]:
    return get_session(user_id).token


def set_profile(user_id: int, profile: Optional[Dict[str, Any]]) -> None:
    session = get_session(user_id)
    session.profile = profile


def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
    return get_session(user_id).profile


def is_authenticated(user_id: int) -> bool:
    """Check if user is authenticated (has valid token)"""
    token = get_token(user_id)
    if not token:
        return False
    
    # Also check database session
    try:
        from app.services.telegram_session_service import get_active_session
        db = SessionLocal()
        try:
            db_session = get_active_session(db, user_id, token)
            if not db_session:
                # Session expired or not found, clear in-memory session
                set_token(user_id, None)
                return False
        finally:
            db.close()
    except Exception:
        # If database check fails, fall back to in-memory check
        pass
    
    return True


__all__ = [
    "UserSession",
    "get_session",
    "clear_session",
    "set_language",
    "get_language",
    "set_token",
    "get_token",
    "set_profile",
    "get_profile",
    "is_authenticated",
    "update_session_activity_in_db",
]

