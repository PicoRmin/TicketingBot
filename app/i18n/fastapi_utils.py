"""
FastAPI helpers for i18n.
"""
from typing import Optional

from fastapi import Request

from app.core.enums import Language
from app.i18n.translator import detect_language_from_accept_header


def resolve_lang(request: Request, user: Optional[object] = None) -> Language:
    """
    Resolve language preference:
    1) If user has `language` attribute, use it.
    2) Else use Accept-Language header.
    3) Default to FA.
    """
    if user is not None:
        user_lang = getattr(user, "language", None)
        if user_lang:
            try:
                return Language(user_lang)
            except ValueError:
                pass
    return detect_language_from_accept_header(request.headers.get("accept-language"))


__all__ = ["resolve_lang"]

