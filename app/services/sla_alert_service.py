"""
SLA Alert Service - بررسی و ارسال هشدارهای SLA
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.models import SLALog, Ticket, User, SLARule
from app.core.enums import TicketStatus, UserRole
from app.services.notification_service import (
    send_telegram_notification_to_user,
    send_telegram_notification_to_role
)
import asyncio

logger = logging.getLogger(__name__)


def _get_priority_label(priority) -> str:
    """Get priority label in Persian"""
    if not priority:
        return "نامشخص"
    if hasattr(priority, 'value'):
        priority_value = priority.value
    else:
        priority_value = str(priority)
    
    priority_map = {
        "critical": "🔴 بحرانی",
        "high": "🟠 بالا",
        "medium": "🟡 متوسط",
        "low": "🟢 پایین"
    }
    return priority_map.get(priority_value.lower(), priority_value)


async def check_sla_warnings_and_breaches(db: Session) -> Dict[str, Any]:
    """
    بررسی تیکت‌ها برای هشدارها و نقض‌های SLA
    و ارسال اعلان‌های لازم
    
    Returns:
        Dict با آمار بررسی شده
    """
    now = datetime.utcnow()
    stats = {
        "checked": 0,
        "warnings_sent": 0,
        "breaches_sent": 0,
        "escalations_sent": 0,
        "errors": 0
    }
    
    try:
        # دریافت تمام SLA Logs فعال که هنوز حل نشده‌اند
        active_tickets_query = db.query(Ticket).filter(
            Ticket.status.in_([TicketStatus.PENDING, TicketStatus.IN_PROGRESS])
        )
        
        sla_logs = (
            db.query(SLALog)
            .join(Ticket)
            .options(joinedload(SLALog.ticket), joinedload(SLALog.sla_rule))
            .filter(
                Ticket.status.in_([TicketStatus.PENDING, TicketStatus.IN_PROGRESS])
            )
            .all()
        )
        
        stats["checked"] = len(sla_logs)
        
        for sla_log in sla_logs:
            try:
                ticket = sla_log.ticket
                sla_rule = sla_log.sla_rule
                
                if not ticket or not sla_rule:
                    continue
                
                # بررسی وضعیت پاسخ
                response_warning_sent = await _check_response_warning(db, sla_log, ticket, sla_rule, now)
                if response_warning_sent:
                    stats["warnings_sent"] += 1
                
                response_breach_sent = await _check_response_breach(db, sla_log, ticket, sla_rule, now)
                if response_breach_sent:
                    stats["breaches_sent"] += 1
                
                # بررسی وضعیت حل
                resolution_warning_sent = await _check_resolution_warning(db, sla_log, ticket, sla_rule, now)
                if resolution_warning_sent:
                    stats["warnings_sent"] += 1
                
                resolution_breach_sent = await _check_resolution_breach(db, sla_log, ticket, sla_rule, now)
                if resolution_breach_sent:
                    stats["breaches_sent"] += 1
                
                # بررسی Escalation
                escalation_sent = await _check_escalation(db, sla_log, ticket, sla_rule, now)
                if escalation_sent:
                    stats["escalations_sent"] += 1
                
            except Exception as e:
                logger.error(f"Error checking SLA for ticket {sla_log.ticket_id}: {e}", exc_info=True)
                stats["errors"] += 1
        
        logger.info(f"SLA check completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error in check_sla_warnings_and_breaches: {e}", exc_info=True)
        stats["errors"] += 1
        return stats


async def _check_response_warning(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket,
    sla_rule: SLARule,
    now: datetime
) -> bool:
    """
    بررسی هشدار برای زمان پاسخ
    Returns True if warning was sent
    """
    # اگر قبلاً پاسخ داده شده، نیازی به بررسی نیست
    if ticket.first_response_at:
        return False
    
    # محاسبه زمان هشدار
    warning_time = sla_log.target_response_time - timedelta(minutes=sla_rule.response_warning_minutes)
    
    # بررسی اینکه آیا در منطقه هشدار هستیم
    if warning_time <= now < sla_log.target_response_time:
        # بررسی اینکه آیا قبلاً هشدار ارسال شده (برای جلوگیری از ارسال مکرر)
        # می‌توانیم از response_status استفاده کنیم
        if sla_log.response_status != "warning":
            # به‌روزرسانی وضعیت
            sla_log.response_status = "warning"
            db.commit()
            
            # ارسال اعلان
            await _send_response_warning_notification(ticket, sla_log, sla_rule)
            return True
    
    return False


async def _check_response_breach(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket,
    sla_rule: SLARule,
    now: datetime
) -> bool:
    """
    بررسی نقض برای زمان پاسخ
    Returns True if breach notification was sent
    """
    # اگر قبلاً پاسخ داده شده، نیازی به بررسی نیست
    if ticket.first_response_at:
        return False
    
    # بررسی اینکه آیا مهلت گذشته است
    if now >= sla_log.target_response_time:
        # بررسی اینکه آیا قبلاً نقض ثبت شده
        if sla_log.response_status != "breached":
            # به‌روزرسانی وضعیت
            sla_log.response_status = "breached"
            db.commit()
            
            # ارسال اعلان
            await _send_response_breach_notification(ticket, sla_log, sla_rule)
            return True
    
    return False


async def _check_resolution_warning(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket,
    sla_rule: SLARule,
    now: datetime
) -> bool:
    """
    بررسی هشدار برای زمان حل
    Returns True if warning was sent
    """
    # اگر قبلاً حل شده، نیازی به بررسی نیست
    if ticket.resolved_at or ticket.closed_at:
        return False
    
    # محاسبه زمان هشدار
    warning_time = sla_log.target_resolution_time - timedelta(minutes=sla_rule.resolution_warning_minutes)
    
    # بررسی اینکه آیا در منطقه هشدار هستیم
    if warning_time <= now < sla_log.target_resolution_time:
        # بررسی اینکه آیا قبلاً هشدار ارسال شده
        if sla_log.resolution_status != "warning":
            # به‌روزرسانی وضعیت
            sla_log.resolution_status = "warning"
            db.commit()
            
            # ارسال اعلان
            await _send_resolution_warning_notification(ticket, sla_log, sla_rule)
            return True
    
    return False


async def _check_resolution_breach(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket,
    sla_rule: SLARule,
    now: datetime
) -> bool:
    """
    بررسی نقض برای زمان حل
    Returns True if breach notification was sent
    """
    # اگر قبلاً حل شده، نیازی به بررسی نیست
    if ticket.resolved_at or ticket.closed_at:
        return False
    
    # بررسی اینکه آیا مهلت گذشته است
    if now >= sla_log.target_resolution_time:
        # بررسی اینکه آیا قبلاً نقض ثبت شده
        if sla_log.resolution_status != "breached":
            # به‌روزرسانی وضعیت
            sla_log.resolution_status = "breached"
            db.commit()
            
            # ارسال اعلان
            await _send_resolution_breach_notification(ticket, sla_log, sla_rule)
            return True
    
    return False


async def _check_escalation(
    db: Session,
    sla_log: SLALog,
    ticket: Ticket,
    sla_rule: SLARule,
    now: datetime
) -> bool:
    """
    بررسی نیاز به Escalation
    Returns True if escalation was sent
    """
    # بررسی اینکه آیا Escalation فعال است
    if not sla_rule.escalation_enabled or not sla_rule.escalation_after_minutes:
        return False
    
    # بررسی اینکه آیا قبلاً Escalation انجام شده
    if sla_log.escalated:
        return False
    
    # محاسبه زمان Escalation
    escalation_time = ticket.created_at + timedelta(minutes=sla_rule.escalation_after_minutes)
    
    # بررسی اینکه آیا زمان Escalation رسیده است
    if now >= escalation_time:
        # به‌روزرسانی وضعیت
        sla_log.escalated = True
        sla_log.escalated_at = now
        db.commit()
        
        # ارسال اعلان Escalation
        await _send_escalation_notification(ticket, sla_log, sla_rule)
        return True
    
    return False


async def _send_response_warning_notification(ticket: Ticket, sla_log: SLALog, sla_rule: SLARule):
    """
    ارسال اعلان هشدار برای زمان پاسخ
    Send response time warning notification
    """
    try:
        from app.services.email_service import email_service
        from app.core.enums import Language
        from app.i18n.translator import translate
        
        # محاسبه زمان باقی‌مانده
        remaining_minutes = int((sla_log.target_response_time - datetime.utcnow()).total_seconds() / 60)
        remaining_time = f"{remaining_minutes} دقیقه"
        if remaining_minutes >= 60:
            hours = remaining_minutes // 60
            mins = remaining_minutes % 60
            remaining_time = f"{hours} ساعت و {mins} دقیقه"
        
        message = (
            f"⚠️ <b>هشدار SLA - زمان پاسخ</b>\n\n"
            f"🔹 تیکت: <b>{ticket.ticket_number}</b>\n"
            f"📌 عنوان: {ticket.title}\n"
            f"🚨 اولویت: {_get_priority_label(sla_rule.priority)}\n"
            f"⏰ زمان باقی‌مانده: {remaining_time}\n"
            f"📅 مهلت پاسخ: {sla_log.target_response_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"لطفاً در اسرع وقت به این تیکت پاسخ دهید."
        )
        
        # ارسال به کارشناس مسئول
        if ticket.assigned_to:
            if ticket.assigned_to.telegram_chat_id:
                await send_telegram_notification_to_user(ticket.assigned_to.telegram_chat_id, message)
            
            # ارسال ایمیل
            if ticket.assigned_to.email:
                try:
                    lang = ticket.assigned_to.language if hasattr(ticket.assigned_to, 'language') else Language.FA
                    await email_service.send_sla_warning_email(
                        to_email=ticket.assigned_to.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        warning_type='response',
                        remaining_time=remaining_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA warning to assigned user {ticket.assigned_to.id}: {e}")
        
        # ارسال به مدیران
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            await send_telegram_notification_to_role(db, UserRole.ADMIN, message)
            await send_telegram_notification_to_role(db, UserRole.CENTRAL_ADMIN, message)
            
            # ارسال ایمیل به مدیران
            from app.models import User
            admins = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.CENTRAL_ADMIN]),
                User.is_active == True,
                User.email.isnot(None)
            ).all()
            
            for admin in admins:
                try:
                    lang = admin.language if hasattr(admin, 'language') else Language.FA
                    await email_service.send_sla_warning_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        warning_type='response',
                        remaining_time=remaining_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA warning to admin {admin.id}: {e}")
        finally:
            db.close()
        
        logger.info(f"Response warning sent for ticket {ticket.ticket_number}")
        
    except Exception as e:
        logger.error(f"Error sending response warning notification: {e}", exc_info=True)


async def _send_response_breach_notification(ticket: Ticket, sla_log: SLALog, sla_rule: SLARule):
    """
    ارسال اعلان نقض برای زمان پاسخ
    Send response time breach notification
    """
    try:
        from app.services.email_service import email_service
        from app.core.enums import Language
        
        # محاسبه زمان تاخیر
        delay_minutes = int((datetime.utcnow() - sla_log.target_response_time).total_seconds() / 60)
        delay_time = f"{delay_minutes} دقیقه"
        if delay_minutes >= 60:
            hours = delay_minutes // 60
            mins = delay_minutes % 60
            delay_time = f"{hours} ساعت و {mins} دقیقه"
        
        message = (
            f"🔴 <b>نقض SLA - زمان پاسخ</b>\n\n"
            f"🔹 تیکت: <b>{ticket.ticket_number}</b>\n"
            f"📌 عنوان: {ticket.title}\n"
            f"🚨 اولویت: {_get_priority_label(sla_rule.priority)}\n"
            f"⏰ تاخیر: {delay_time}\n"
            f"📅 مهلت پاسخ: {sla_log.target_response_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"⚠️ این تیکت از مهلت پاسخ خود گذشته است. لطفاً فوراً رسیدگی کنید."
        )
        
        # ارسال به کارشناس مسئول
        if ticket.assigned_to:
            if ticket.assigned_to.telegram_chat_id:
                await send_telegram_notification_to_user(ticket.assigned_to.telegram_chat_id, message)
            
            # ارسال ایمیل
            if ticket.assigned_to.email:
                try:
                    lang = ticket.assigned_to.language if hasattr(ticket.assigned_to, 'language') else Language.FA
                    await email_service.send_sla_breach_email(
                        to_email=ticket.assigned_to.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        breach_type='response',
                        delay_time=delay_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA breach to assigned user {ticket.assigned_to.id}: {e}")
        
        # ارسال به مدیران
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            await send_telegram_notification_to_role(db, UserRole.ADMIN, message)
            await send_telegram_notification_to_role(db, UserRole.CENTRAL_ADMIN, message)
            
            # ارسال ایمیل به مدیران
            from app.models import User
            admins = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.CENTRAL_ADMIN]),
                User.is_active == True,
                User.email.isnot(None)
            ).all()
            
            for admin in admins:
                try:
                    lang = admin.language if hasattr(admin, 'language') else Language.FA
                    await email_service.send_sla_breach_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        breach_type='response',
                        delay_time=delay_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA breach to admin {admin.id}: {e}")
        finally:
            db.close()
        
        logger.info(f"Response breach notification sent for ticket {ticket.ticket_number}")
        
    except Exception as e:
        logger.error(f"Error sending response breach notification: {e}", exc_info=True)


async def _send_resolution_warning_notification(ticket: Ticket, sla_log: SLALog, sla_rule: SLARule):
    """
    ارسال اعلان هشدار برای زمان حل
    Send resolution time warning notification
    """
    try:
        from app.services.email_service import email_service
        from app.core.enums import Language
        
        # محاسبه زمان باقی‌مانده
        remaining_minutes = int((sla_log.target_resolution_time - datetime.utcnow()).total_seconds() / 60)
        remaining_time = f"{remaining_minutes} دقیقه"
        if remaining_minutes >= 60:
            hours = remaining_minutes // 60
            mins = remaining_minutes % 60
            remaining_time = f"{hours} ساعت و {mins} دقیقه"
        
        message = (
            f"⚠️ <b>هشدار SLA - زمان حل</b>\n\n"
            f"🔹 تیکت: <b>{ticket.ticket_number}</b>\n"
            f"📌 عنوان: {ticket.title}\n"
            f"🚨 اولویت: {_get_priority_label(sla_rule.priority)}\n"
            f"⏰ زمان باقی‌مانده: {remaining_time}\n"
            f"📅 مهلت حل: {sla_log.target_resolution_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"لطفاً در اسرع وقت این تیکت را حل کنید."
        )
        
        # ارسال به کارشناس مسئول
        if ticket.assigned_to:
            if ticket.assigned_to.telegram_chat_id:
                await send_telegram_notification_to_user(ticket.assigned_to.telegram_chat_id, message)
            
            # ارسال ایمیل
            if ticket.assigned_to.email:
                try:
                    lang = ticket.assigned_to.language if hasattr(ticket.assigned_to, 'language') else Language.FA
                    await email_service.send_sla_warning_email(
                        to_email=ticket.assigned_to.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        warning_type='resolution',
                        remaining_time=remaining_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA warning to assigned user {ticket.assigned_to.id}: {e}")
        
        # ارسال به مدیران
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            await send_telegram_notification_to_role(db, UserRole.ADMIN, message)
            await send_telegram_notification_to_role(db, UserRole.CENTRAL_ADMIN, message)
            
            # ارسال ایمیل به مدیران
            from app.models import User
            admins = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.CENTRAL_ADMIN]),
                User.is_active == True,
                User.email.isnot(None)
            ).all()
            
            for admin in admins:
                try:
                    lang = admin.language if hasattr(admin, 'language') else Language.FA
                    await email_service.send_sla_warning_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        warning_type='resolution',
                        remaining_time=remaining_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA warning to admin {admin.id}: {e}")
        finally:
            db.close()
        
        logger.info(f"Resolution warning sent for ticket {ticket.ticket_number}")
        
    except Exception as e:
        logger.error(f"Error sending resolution warning notification: {e}", exc_info=True)


async def _send_resolution_breach_notification(ticket: Ticket, sla_log: SLALog, sla_rule: SLARule):
    """
    ارسال اعلان نقض برای زمان حل
    Send resolution time breach notification
    """
    try:
        from app.services.email_service import email_service
        from app.core.enums import Language
        
        # محاسبه زمان تاخیر
        delay_minutes = int((datetime.utcnow() - sla_log.target_resolution_time).total_seconds() / 60)
        delay_time = f"{delay_minutes} دقیقه"
        if delay_minutes >= 60:
            hours = delay_minutes // 60
            mins = delay_minutes % 60
            delay_time = f"{hours} ساعت و {mins} دقیقه"
        
        message = (
            f"🔴 <b>نقض SLA - زمان حل</b>\n\n"
            f"🔹 تیکت: <b>{ticket.ticket_number}</b>\n"
            f"📌 عنوان: {ticket.title}\n"
            f"🚨 اولویت: {_get_priority_label(sla_rule.priority)}\n"
            f"⏰ تاخیر: {delay_time}\n"
            f"📅 مهلت حل: {sla_log.target_resolution_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"⚠️ این تیکت از مهلت حل خود گذشته است. لطفاً فوراً رسیدگی کنید."
        )
        
        # ارسال به کارشناس مسئول
        if ticket.assigned_to:
            if ticket.assigned_to.telegram_chat_id:
                await send_telegram_notification_to_user(ticket.assigned_to.telegram_chat_id, message)
            
            # ارسال ایمیل
            if ticket.assigned_to.email:
                try:
                    lang = ticket.assigned_to.language if hasattr(ticket.assigned_to, 'language') else Language.FA
                    await email_service.send_sla_breach_email(
                        to_email=ticket.assigned_to.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        breach_type='resolution',
                        delay_time=delay_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA breach to assigned user {ticket.assigned_to.id}: {e}")
        
        # ارسال به مدیران
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            await send_telegram_notification_to_role(db, UserRole.ADMIN, message)
            await send_telegram_notification_to_role(db, UserRole.CENTRAL_ADMIN, message)
            
            # ارسال ایمیل به مدیران
            from app.models import User
            admins = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.CENTRAL_ADMIN]),
                User.is_active == True,
                User.email.isnot(None)
            ).all()
            
            for admin in admins:
                try:
                    lang = admin.language if hasattr(admin, 'language') else Language.FA
                    await email_service.send_sla_breach_email(
                        to_email=admin.email,
                        ticket_number=ticket.ticket_number,
                        ticket_title=ticket.title,
                        breach_type='resolution',
                        delay_time=delay_time,
                        language=lang
                    )
                except Exception as e:
                    logger.error(f"Failed to send email SLA breach to admin {admin.id}: {e}")
        finally:
            db.close()
        
        logger.info(f"Resolution breach notification sent for ticket {ticket.ticket_number}")
        
    except Exception as e:
        logger.error(f"Error sending resolution breach notification: {e}", exc_info=True)


async def _send_escalation_notification(ticket: Ticket, sla_log: SLALog, sla_rule: SLARule):
    """ارسال اعلان Escalation"""
    try:
        message = (
            f"📈 <b>Escalation SLA</b>\n\n"
            f"🔹 تیکت: <b>{ticket.ticket_number}</b>\n"
            f"📌 عنوان: {ticket.title}\n"
            f"🚨 اولویت: {_get_priority_label(sla_rule.priority)}\n"
            f"⏰ زمان Escalation: {sla_log.escalated_at.strftime('%Y-%m-%d %H:%M') if sla_log.escalated_at else 'نامشخص'}\n\n"
            f"این تیکت به سطح بالاتر ارجاع داده شده است. لطفاً فوراً رسیدگی کنید."
        )
        
        # ارسال به مدیران ارشد
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            await send_telegram_notification_to_role(db, UserRole.CENTRAL_ADMIN, message)
            await send_telegram_notification_to_role(db, UserRole.ADMIN, message)
        finally:
            db.close()
        
        logger.info(f"Escalation notification sent for ticket {ticket.ticket_number}")
        
    except Exception as e:
        logger.error(f"Error sending escalation notification: {e}", exc_info=True)

