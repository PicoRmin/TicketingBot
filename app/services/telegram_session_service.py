"""
Service for managing Telegram bot sessions
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.telegram_session import TelegramSession
from app.models.user import User
from app.config import settings


# Session timeout from settings
SESSION_TIMEOUT_MINUTES = settings.TELEGRAM_SESSION_TIMEOUT_MINUTES


def create_session(
    db: Session,
    user_id: int,
    telegram_user_id: int,
    token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TelegramSession:
    """
    Create a new Telegram session
    
    Args:
        db: Database session
        user_id: Backend user ID
        telegram_user_id: Telegram user ID
        token: JWT access token
        ip_address: IP address (optional)
        user_agent: User agent string (optional)
        
    Returns:
        Created TelegramSession
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    
    session = TelegramSession(
        user_id=user_id,
        telegram_user_id=telegram_user_id,
        token=token,
        ip_address=ip_address,
        user_agent=user_agent,
        last_activity=now,
        created_at=now,
        expires_at=expires_at,
        is_active=1,
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session_activity(
    db: Session,
    telegram_user_id: int,
    token: str,
) -> Optional[TelegramSession]:
    """
    Update last activity timestamp for a session
    
    Args:
        db: Database session
        telegram_user_id: Telegram user ID
        token: JWT access token
        
    Returns:
        Updated TelegramSession or None if not found
    """
    session = db.query(TelegramSession).filter(
        and_(
            TelegramSession.telegram_user_id == telegram_user_id,
            TelegramSession.token == token,
            TelegramSession.is_active == 1,
        )
    ).first()
    
    if session:
        now = datetime.now(timezone.utc)
        # Extend expiration time on activity
        session.expires_at = now + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        session.last_activity = now
        db.commit()
        db.refresh(session)
    
    return session


def get_active_session(
    db: Session,
    telegram_user_id: int,
    token: str,
) -> Optional[TelegramSession]:
    """
    Get active session for a user
    
    Args:
        db: Database session
        telegram_user_id: Telegram user ID
        token: JWT access token
        
    Returns:
        Active TelegramSession or None if not found/expired
    """
    session = db.query(TelegramSession).filter(
        and_(
            TelegramSession.telegram_user_id == telegram_user_id,
            TelegramSession.token == token,
            TelegramSession.is_active == 1,
        )
    ).first()
    
    if session and not session.is_expired():
        return session
    
    # Mark expired sessions as inactive
    if session and session.is_expired():
        session.is_active = 0
        db.commit()
    
    return None


def get_user_sessions(
    db: Session,
    user_id: int,
    active_only: bool = True,
) -> List[TelegramSession]:
    """
    Get all sessions for a user
    
    Args:
        db: Database session
        user_id: Backend user ID
        active_only: If True, only return active sessions
        
    Returns:
        List of TelegramSession objects
    """
    query = db.query(TelegramSession).filter(
        TelegramSession.user_id == user_id
    )
    
    if active_only:
        query = query.filter(TelegramSession.is_active == 1)
    
    # Filter out expired sessions
    now = datetime.now(timezone.utc)
    sessions = query.all()
    active_sessions = []
    
    for session in sessions:
        if session.is_expired():
            session.is_active = 0
            db.commit()
        elif session.is_active == 1:
            active_sessions.append(session)
    
    return active_sessions


def logout_session(
    db: Session,
    telegram_user_id: int,
    token: str,
) -> bool:
    """
    Logout a specific session
    
    Args:
        db: Database session
        telegram_user_id: Telegram user ID
        token: JWT access token
        
    Returns:
        True if session was found and logged out, False otherwise
    """
    session = db.query(TelegramSession).filter(
        and_(
            TelegramSession.telegram_user_id == telegram_user_id,
            TelegramSession.token == token,
            TelegramSession.is_active == 1,
        )
    ).first()
    
    if session:
        session.is_active = 0
        db.commit()
        return True
    
    return False


def logout_all_sessions(
    db: Session,
    user_id: int,
) -> int:
    """
    Logout all sessions for a user
    
    Args:
        db: Database session
        user_id: Backend user ID
        
    Returns:
        Number of sessions logged out
    """
    sessions = db.query(TelegramSession).filter(
        and_(
            TelegramSession.user_id == user_id,
            TelegramSession.is_active == 1,
        )
    ).all()
    
    count = len(sessions)
    for session in sessions:
        session.is_active = 0
    
    db.commit()
    return count


def cleanup_expired_telegram_sessions(db: Session) -> int:
    """
    Clean up expired Telegram sessions (mark as inactive)
    
    Args:
        db: Database session
        
    Returns:
        Number of sessions cleaned up
    """
    now = datetime.now(timezone.utc)
    sessions = db.query(TelegramSession).filter(
        and_(
            TelegramSession.is_active == 1,
            TelegramSession.expires_at < now,
        )
    ).all()
    
    count = len(sessions)
    for session in sessions:
        session.is_active = 0
    
    db.commit()
    return count


def format_session_info(session: TelegramSession, language: str = "fa") -> str:
    """
    Format session information for display
    
    Args:
        session: TelegramSession object
        language: Language code (fa/en)
        
    Returns:
        Formatted string
    """
    if language == "en":
        ip_info = f"IP: {session.ip_address or 'Unknown'}" if session.ip_address else "IP: Unknown"
        created = session.created_at.strftime("%Y-%m-%d %H:%M:%S") if session.created_at else "Unknown"
        last_activity = session.last_activity.strftime("%Y-%m-%d %H:%M:%S") if session.last_activity else "Unknown"
        
        return (
            f"🕐 Created: {created}\n"
            f"⏰ Last Activity: {last_activity}\n"
            f"🌐 {ip_info}"
        )
    else:
        ip_info = f"IP: {session.ip_address or 'نامشخص'}" if session.ip_address else "IP: نامشخص"
        created = session.created_at.strftime("%Y-%m-%d %H:%M:%S") if session.created_at else "نامشخص"
        last_activity = session.last_activity.strftime("%Y-%m-%d %H:%M:%S") if session.last_activity else "نامشخص"
        
        return (
            f"🕐 ایجاد شده: {created}\n"
            f"⏰ آخرین فعالیت: {last_activity}\n"
            f"🌐 {ip_info}"
        )

