"""
سرویس مدیریت کامنت‌های تیکت
Comment service for ticket comments
"""
from typing import List
from sqlalchemy.orm import Session
from app.models import Comment, Ticket, User
from app.schemas.comment import CommentCreate
import logging

logger = logging.getLogger(__name__)


async def create_comment(db: Session, user_id: int, data: CommentCreate) -> Comment:
  """
  ایجاد کامنت جدید برای تیکت
  Create a new comment for a ticket
  
  Args:
      db: Session دیتابیس
      user_id: شناسه کاربر ایجادکننده کامنت
      data: داده‌های کامنت
  
  Returns:
      Comment: کامنت ایجاد شده
  """
  from app.services.email_service import email_service
  from app.core.enums import Language
  
  comment = Comment(
    ticket_id=data.ticket_id,
    user_id=user_id,
    comment=data.comment,
    is_internal=data.is_internal,
  )
  db.add(comment)
  db.commit()
  db.refresh(comment)
  
  # ارسال اعلان ایمیل (فقط برای کامنت‌های عمومی)
  if not data.is_internal:
    try:
      # دریافت تیکت و کاربران مرتبط
      ticket = db.query(Ticket).filter(Ticket.id == data.ticket_id).first()
      comment_author = db.query(User).filter(User.id == user_id).first()
      
      if ticket and comment_author:
        # ارسال به صاحب تیکت (اگر خودش کامنت نگذاشته باشد)
        if ticket.user and ticket.user.id != user_id and ticket.user.email:
          try:
            lang = ticket.user.language if hasattr(ticket.user, 'language') else Language.FA
            await email_service.send_comment_added_email(
              to_email=ticket.user.email,
              ticket_number=ticket.ticket_number,
              ticket_title=ticket.title,
              comment_author=comment_author.full_name,
              comment_text=data.comment[:500],  # محدود کردن طول متن
              language=lang
            )
          except Exception as e:
            logger.error(f"Failed to send email to ticket owner: {e}")
        
        # ارسال به کارشناس مسئول (اگر خودش کامنت نگذاشته باشد)
        if ticket.assigned_to and ticket.assigned_to.id != user_id and ticket.assigned_to.email:
          try:
            lang = ticket.assigned_to.language if hasattr(ticket.assigned_to, 'language') else Language.FA
            await email_service.send_comment_added_email(
              to_email=ticket.assigned_to.email,
              ticket_number=ticket.ticket_number,
              ticket_title=ticket.title,
              comment_author=comment_author.full_name,
              comment_text=data.comment[:500],
              language=lang
            )
          except Exception as e:
            logger.error(f"Failed to send email to assigned user: {e}")
    except Exception as e:
      logger.error(f"Error sending comment notification emails: {e}", exc_info=True)
  
  return comment


def list_ticket_comments(db: Session, ticket_id: int, include_internal: bool = False) -> List[Comment]:
  q = db.query(Comment).filter(Comment.ticket_id == ticket_id)
  if not include_internal:
    q = q.filter(Comment.is_internal == False)  # noqa: E712
  return q.order_by(Comment.created_at.asc()).all()

