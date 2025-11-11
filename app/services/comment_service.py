from typing import List
from sqlalchemy.orm import Session
from app.models import Comment
from app.schemas.comment import CommentCreate


def create_comment(db: Session, user_id: int, data: CommentCreate) -> Comment:
  comment = Comment(
    ticket_id=data.ticket_id,
    user_id=user_id,
    comment=data.comment,
    is_internal=data.is_internal,
  )
  db.add(comment)
  db.commit()
  db.refresh(comment)
  return comment


def list_ticket_comments(db: Session, ticket_id: int, include_internal: bool = False) -> List[Comment]:
  q = db.query(Comment).filter(Comment.ticket_id == ticket_id)
  if not include_internal:
    q = q.filter(Comment.is_internal == False)  # noqa: E712
  return q.order_by(Comment.created_at.asc()).all()

