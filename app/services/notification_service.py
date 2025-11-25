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
from app.services.email_service import email_service

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
    """
    اطلاع‌رسانی ایجاد تیکت به صاحب تیکت و ادمین‌ها
    Notify ticket owner and admins about new ticket
    """
    try:
        messages: List[Tuple[str, str]] = []

        creator = ticket.user
        creator_language = _normalize_language(creator.language if creator else None)
        
        # ارسال اعلان تلگرام به کاربر
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
        
        # ارسال ایمیل به کاربر (اگر ایمیل داشته باشد)
        if creator and creator.email:
            try:
                category_label = _ticket_category_label(
                    ticket.category.value if hasattr(ticket.category, 'value') else ticket.category,
                    creator_language
                )
                await email_service.send_ticket_created_email(
                    to_email=creator.email,
                    ticket_number=ticket.ticket_number,
                    ticket_title=ticket.title,
                    ticket_category=category_label,
                    language=creator_language
                )
            except Exception as e:
                logger.error(f"Failed to send email notification to user {creator.id}: {e}")

        # ارسال اعلان به ادمین‌ها
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
            
            # ارسال ایمیل به ادمین (اگر ایمیل داشته باشد)
            if admin.email:
                try:
                    category_label = _ticket_category_label(
                        ticket.category.value if hasattr(ticket.category, 'value') else ticket.category,
                        lang
                    )
                    await email_service.send_ticket_created_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        ticket_category=category_label,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification to admin {admin.id}: {e}")

        if messages:
            await _send_telegram_messages(messages)
    except Exception as exc:
        logger.exception("Error in notify_ticket_created: %s", exc)


async def notify_ticket_status_changed(
    ticket: Ticket,
    previous_status: TicketStatus,
    db: Session,
) -> None:
    """
    اطلاع‌رسانی تغییر وضعیت تیکت به صاحب تیکت و ادمین‌ها
    Notify ticket owner about status change and alert admins
    """
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
        
        # ارسال ایمیل به کاربر (اگر ایمیل داشته باشد)
        if creator and creator.email:
            try:
                lang = _normalize_language(creator.language)
                previous_status_label = _status_label(previous_status, lang)
                new_status_label = _status_label(ticket.status, lang)
                await email_service.send_ticket_status_changed_email(
                    to_email=creator.email,
                    ticket_number=ticket.ticket_number,
                    ticket_title=ticket.title,
                    previous_status=previous_status_label,
                    new_status=new_status_label,
                    language=lang
                )
            except Exception as e:
                logger.error(f"Failed to send email notification to user {creator.id}: {e}")

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
            
            # ارسال ایمیل به ادمین (اگر ایمیل داشته باشد)
            if admin.email:
                try:
                    previous_status_label = _status_label(previous_status, lang)
                    new_status_label = _status_label(ticket.status, lang)
                    await email_service.send_ticket_status_changed_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        previous_status=previous_status_label,
                        new_status=new_status_label,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification to admin {admin.id}: {e}")

        if messages:
            await _send_telegram_messages(messages)
    except Exception as exc:
        logger.exception("Error in notify_ticket_status_changed: %s", exc)


async def send_telegram_notification_to_user(chat_id: str, message: str) -> None:
    """
    ارسال اعلان تلگرام به یک کاربر خاص
    
    Args:
        chat_id: شناسه چت تلگرام کاربر
        message: متن پیام
    """
    if not chat_id or not message:
        return
    
    try:
        await _send_telegram_messages([(chat_id, message)])
    except Exception as exc:
        logger.exception("Error sending telegram notification to user: %s", exc)


async def notify_ticket_assigned(
    ticket: Ticket,
    assigned_by: User,
    db: Session
) -> None:
    """
    اطلاع‌رسانی تخصیص تیکت به کاربر تخصیص داده شده
    Notify user about ticket assignment
    """
    if not ticket.assigned_to:
        return
    
    try:
        assigned_user = ticket.assigned_to
        lang = _normalize_language(assigned_user.language)
        
        # ارسال اعلان تلگرام
        if assigned_user.telegram_chat_id:
            text = translate(
                "notifications.ticket_assigned",
                lang,
            ) or "A ticket has been assigned to you."
            text += (
                f"\n\n<strong>{ticket.ticket_number}</strong>"
                f"\n{ticket.title}"
                f"\n👤 تخصیص داده شده توسط: {assigned_by.full_name if assigned_by else 'سیستم'}"
            )
            await _send_telegram_messages([(assigned_user.telegram_chat_id, text)])
        
        # ارسال ایمیل
        if assigned_user.email:
            try:
                await email_service.send_ticket_assigned_email(
                    to_email=assigned_user.email,
                    ticket_number=ticket.ticket_number,
                    ticket_title=ticket.title,
                    assigned_by=assigned_by.full_name if assigned_by else "سیستم",
                    language=lang
                )
            except Exception as e:
                logger.error(f"Failed to send email notification to assigned user {assigned_user.id}: {e}")
    except Exception as exc:
        logger.exception("Error in notify_ticket_assigned: %s", exc)


async def send_telegram_notification_to_role(
    db: Session | None,
    role: UserRole,
    message: str
) -> None:
    """
    ارسال اعلان تلگرام به تمام کاربران با یک نقش خاص
    
    Args:
        db: Session دیتابیس (اگر None باشد، از SessionLocal استفاده می‌شود)
        role: نقش کاربران
        message: متن پیام
    """
    if not message:
        return
    
    try:
        if db is None:
            from app.database import SessionLocal
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            users = (
                db.query(User)
                .filter(
                    User.role == role,
                    User.is_active.is_(True),
                    User.telegram_chat_id.isnot(None)
                )
                .all()
            )
            
            messages = [(user.telegram_chat_id, message) for user in users if user.telegram_chat_id]
            
            if messages:
                await _send_telegram_messages(messages)
        finally:
            if should_close:
                db.close()
    except Exception as exc:
        logger.exception("Error sending telegram notification to role: %s", exc)