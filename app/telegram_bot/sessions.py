"""
User session management for the Telegram bot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.core.enums import Language


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
    return get_token(user_id) is not None


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
]

