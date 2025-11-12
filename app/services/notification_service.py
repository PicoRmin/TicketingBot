"""Notification helpers for tickets."""
from __future__ import annotations

import asyncio
import logging
from typing import Iterable, List, Tuple

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import Language, TicketStatus, UserRole
from app.i18n.translator import translate
from app.models import Ticket, User

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org"


def _status_label(status: TicketStatus, language: Language) -> str:
    key = f"notifications.status.{status.value.lower()}"
    return translate(key, language) or status.name.replace("_", " ")


def _ticket_category_label(category: str, language: Language) -> str:
    key = f"notifications.category.{category.lower()}"
    return translate(key, language) or category


async def _send_telegram_messages(messages: Iterable[Tuple[str, str]]) -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.debug("Telegram bot token not set; skipping notifications")
        return

    payloads = [(chat_id, text) for chat_id, text in messages if chat_id and text]
    if not payloads:
        return

    url = f"{TELEGRAM_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for chat_id, text in payloads:
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            tasks.append(client.post(url, json=data))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Telegram notification failed: %s", result)


def _collect_admin_recipients(db: Session, exclude_user_id: int | None = None) -> List[User]:
    query = (
        db.query(User)
        .filter(
            User.role == UserRole.ADMIN,
            User.is_active.is_(True),
            User.telegram_chat_id.isnot(None),
        )
    )
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)
    return query.all()


def _normalize_language(value: Language | str | None) -> Language:
    if isinstance(value, Language):
        return value
    if isinstance(value, str):
        try:
            return Language(value)
        except ValueError:
            return Language.FA
    return Language.FA


async def notify_ticket_created(ticket: Ticket, db: Session) -> None:
    """Notify ticket owner and admins about new ticket."""
    try:
        messages: List[Tuple[str, str]] = []

        creator = ticket.user
        creator_language = _normalize_language(creator.language if creator else None)
        if creator and creator.telegram_chat_id:
            text = translate(
                "notifications.ticket_created_user",
                creator_language,
            ) or "Ticket created successfully."
            text += (
                f"\n\n<strong>{ticket.ticket_number}</strong>"
                f"\n{ticket.title}"
                f"\n{_ticket_category_label(ticket.category.value if hasattr(ticket.category, 'value') else ticket.category, creator_language)}"
            )
            messages.append((creator.telegram_chat_id, text))

        admins = _collect_admin_recipients(db, exclude_user_id=creator.id if creator else None)
        for admin in admins:
            lang = _normalize_language(admin.language)
            text = translate(
                "notifications.ticket_created_admin",
                lang,
            ) or "New ticket created."
            text += (
                f"\n\n<strong>{ticket.ticket_number}</strong>"
                f"\n{ticket.title}"
                f"\n{_ticket_category_label(ticket.category.value if hasattr(ticket.category, 'value') else ticket.category, lang)}"
                f"\n👤 {creator.full_name if creator else '-'}"
            )
            messages.append((admin.telegram_chat_id, text))

        if messages:
            await _send_telegram_messages(messages)
    except Exception as exc:
        logger.exception("Error in notify_ticket_created: %s", exc)


async def notify_ticket_status_changed(
    ticket: Ticket,
    previous_status: TicketStatus,
    db: Session,
) -> None:
    """Notify ticket owner about status change and alert admins."""
    try:
        messages: List[Tuple[str, str]] = []

        creator = ticket.user
        if creator and creator.telegram_chat_id:
            lang = _normalize_language(creator.language)
            text = translate(
                "notifications.ticket_status_user",
                lang,
            ) or "Ticket status updated."
            text += (
                f"\n\n<strong>{ticket.ticket_number}</strong>"
                f"\n{ticket.title}"
                f"\n{_status_label(previous_status, lang)} ➡️ {_status_label(ticket.status, lang)}"
            )
            messages.append((creator.telegram_chat_id, text))

        admins = _collect_admin_recipients(db)
        for admin in admins:
            lang = _normalize_language(admin.language)
            text = translate(
                "notifications.ticket_status_admin",
                lang,
            ) or "Ticket status changed."
            text += (
                f"\n\n<strong>{ticket.ticket_number}</strong>"
                f"\n{ticket.title}"
                f"\n{_status_label(previous_status, lang)} ➡️ {_status_label(ticket.status, lang)}"
                f"\n👤 {creator.full_name if creator else '-'}"
            )
            messages.append((admin.telegram_chat_id, text))

        if messages:
            await _send_telegram_messages(messages)
    except Exception as exc:
        logger.exception("Error in notify_ticket_status_changed: %s", exc)
