"""
Lightweight i18n translator for backend usage.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping

from app.core.enums import Language

_BASE_DIR = Path(__file__).resolve().parent


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=4)
def _get_catalog(lang: Language) -> Mapping[str, Any]:
    filename = "fa.json" if lang == Language.FA else "en.json"
    path = _BASE_DIR / filename
    return _load_json(path)


def translate(key: str, lang: Language = Language.FA, **kwargs: Any) -> str:
    """
    Translate a dotted key like 'auth.login_success' using the given language.
    """
    catalog = _get_catalog(lang)
    parts = key.split(".")
    value: Any = catalog
    for part in parts:
        if isinstance(value, Mapping) and part in value:
            value = value[part]
        else:
            return f"[{key}]"
    if isinstance(value, str):
        try:
            return value.format(**kwargs)
        except Exception:
            return value
    return str(value)


def detect_language_from_accept_header(accept_language: str | None) -> Language:
    """
    Very basic Accept-Language detector: returns EN if it starts with 'en',
    otherwise FA.
    """
    if not accept_language:
        return Language.FA
    lowered = accept_language.lower()
    if lowered.startswith("en"):
        return Language.EN
    return Language.FA


__all__ = ["translate", "detect_language_from_accept_header"]

