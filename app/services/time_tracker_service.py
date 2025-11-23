"""
Time Tracker Service - مدیریت زمان کار روی تیکت‌ها
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import TimeLog, Ticket, User
from app.core.enums import TicketStatus

logger = logging.getLogger(__name__)


def start_timer(db: Session, ticket_id: int, user_id: int, description: Optional[str] = None) -> TimeLog:
    """
    شروع تایمر برای یک تیکت
    
    Args:
        db: Database session
        ticket_id: شناسه تیکت
        user_id: شناسه کاربر
        description: توضیحات (اختیاری)
        
    Returns:
        TimeLog: Time log ایجاد شده
        
    Raises:
        ValueError: اگر تیکت وجود نداشته باشد یا تایمر فعال دیگری وجود داشته باشد
    """
    # بررسی وجود تیکت
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise ValueError("تیکت یافت نشد")
    
    # بررسی اینکه آیا تایمر فعال دیگری برای این کاربر وجود دارد
    active_timer = (
        db.query(TimeLog)
        .filter(
            TimeLog.user_id == user_id,
            TimeLog.is_active == 1,
            TimeLog.end_time.is_(None)
        )
        .first()
    )
    
    if active_timer:
        raise ValueError(f"شما در حال حاضر روی تیکت {active_timer.ticket.ticket_number} کار می‌کنید. لطفاً ابتدا آن را متوقف کنید.")
    
    # ایجاد Time Log جدید
    time_log = TimeLog(
        ticket_id=ticket_id,
        user_id=user_id,
        start_time=datetime.utcnow(),
        description=description,
        is_active=1
    )
    
    db.add(time_log)
    db.commit()
    db.refresh(time_log)
    
    logger.info(f"Timer started for ticket {ticket_id} by user {user_id}")
    return time_log


def stop_timer(db: Session, time_log_id: int, user_id: int, description: Optional[str] = None) -> TimeLog:
    """
    توقف تایمر
    
    Args:
        db: Database session
        time_log_id: شناسه Time Log
        user_id: شناسه کاربر (برای اطمینان از دسترسی)
        description: توضیحات نهایی (اختیاری)
        
    Returns:
        TimeLog: Time log به‌روزرسانی شده
        
    Raises:
        ValueError: اگر Time Log یافت نشود یا متعلق به کاربر نباشد
    """
    time_log = db.query(TimeLog).filter(
        TimeLog.id == time_log_id,
        TimeLog.user_id == user_id
    ).first()
    
    if not time_log:
        raise ValueError("Time log یافت نشد یا شما دسترسی ندارید")
    
    if time_log.end_time:
        raise ValueError("این تایمر قبلاً متوقف شده است")
    
    # محاسبه مدت زمان
    end_time = datetime.utcnow()
    duration = int((end_time - time_log.start_time).total_seconds() / 60)
    
    time_log.end_time = end_time
    time_log.duration_minutes = duration
    time_log.is_active = 0
    
    if description:
        time_log.description = description
    
    db.commit()
    db.refresh(time_log)
    
    logger.info(f"Timer stopped for time_log {time_log_id}, duration: {duration} minutes")
    return time_log


def stop_active_timer(db: Session, user_id: int, description: Optional[str] = None) -> Optional[TimeLog]:
    """
    توقف تایمر فعال کاربر
    
    Args:
        db: Database session
        user_id: شناسه کاربر
        description: توضیحات نهایی (اختیاری)
        
    Returns:
        TimeLog: Time log متوقف شده یا None اگر تایمر فعالی وجود نداشته باشد
    """
    active_timer = (
        db.query(TimeLog)
        .filter(
            TimeLog.user_id == user_id,
            TimeLog.is_active == 1,
            TimeLog.end_time.is_(None)
        )
        .first()
    )
    
    if not active_timer:
        return None
    
    return stop_timer(db, active_timer.id, user_id, description)


def get_active_timer(db: Session, user_id: int) -> Optional[TimeLog]:
    """
    دریافت تایمر فعال کاربر
    
    Args:
        db: Database session
        user_id: شناسه کاربر
        
    Returns:
        TimeLog: تایمر فعال یا None
    """
    return (
        db.query(TimeLog)
        .filter(
            TimeLog.user_id == user_id,
            TimeLog.is_active == 1,
            TimeLog.end_time.is_(None)
        )
        .first()
    )


def get_ticket_time_logs(db: Session, ticket_id: int, user_id: Optional[int] = None) -> List[TimeLog]:
    """
    دریافت تمام Time Logs یک تیکت
    
    Args:
        db: Database session
        ticket_id: شناسه تیکت
        user_id: شناسه کاربر (اختیاری - برای فیلتر)
        
    Returns:
        List[TimeLog]: لیست Time Logs
    """
    query = db.query(TimeLog).filter(TimeLog.ticket_id == ticket_id)
    
    if user_id:
        query = query.filter(TimeLog.user_id == user_id)
    
    return query.order_by(TimeLog.start_time.desc()).all()


def get_user_time_logs(
    db: Session,
    user_id: int,
    ticket_id: Optional[int] = None,
    limit: int = 50
) -> List[TimeLog]:
    """
    دریافت Time Logs یک کاربر
    
    Args:
        db: Database session
        user_id: شناسه کاربر
        ticket_id: شناسه تیکت (اختیاری - برای فیلتر)
        limit: تعداد نتایج
        
    Returns:
        List[TimeLog]: لیست Time Logs
    """
    query = db.query(TimeLog).filter(TimeLog.user_id == user_id)
    
    if ticket_id:
        query = query.filter(TimeLog.ticket_id == ticket_id)
    
    return query.order_by(TimeLog.start_time.desc()).limit(limit).all()


def get_ticket_total_time(db: Session, ticket_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    محاسبه کل زمان کار روی یک تیکت
    
    Args:
        db: Database session
        ticket_id: شناسه تیکت
        user_id: شناسه کاربر (اختیاری - برای فیلتر)
        
    Returns:
        Dict: شامل total_minutes, total_hours, logs_count
    """
    query = db.query(TimeLog).filter(
        TimeLog.ticket_id == ticket_id,
        TimeLog.end_time.isnot(None)  # فقط Time Logs تمام شده
    )
    
    if user_id:
        query = query.filter(TimeLog.user_id == user_id)
    
    logs = query.all()
    
    total_minutes = sum(log.duration_minutes or 0 for log in logs)
    total_hours = total_minutes / 60
    
    return {
        "total_minutes": total_minutes,
        "total_hours": round(total_hours, 2),
        "logs_count": len(logs)
    }


def update_time_log_description(
    db: Session,
    time_log_id: int,
    user_id: int,
    description: str
) -> TimeLog:
    """
    به‌روزرسانی توضیحات Time Log
    
    Args:
        db: Database session
        time_log_id: شناسه Time Log
        user_id: شناسه کاربر
        description: توضیحات جدید
        
    Returns:
        TimeLog: Time log به‌روزرسانی شده
    """
    time_log = db.query(TimeLog).filter(
        TimeLog.id == time_log_id,
        TimeLog.user_id == user_id
    ).first()
    
    if not time_log:
        raise ValueError("Time log یافت نشد یا شما دسترسی ندارید")
    
    time_log.description = description
    db.commit()
    db.refresh(time_log)
    
    return time_log


def delete_time_log(db: Session, time_log_id: int, user_id: int) -> bool:
    """
    حذف Time Log
    
    Args:
        db: Database session
        time_log_id: شناسه Time Log
        user_id: شناسه کاربر
        
    Returns:
        bool: True اگر حذف موفق بود
    """
    time_log = db.query(TimeLog).filter(
        TimeLog.id == time_log_id,
        TimeLog.user_id == user_id
    ).first()
    
    if not time_log:
        return False
    
    try:
        db.delete(time_log)
        db.commit()
        logger.info(f"Time log {time_log_id} deleted by user {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting time log: {e}")
        return False

