from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Ticket, User
from app.schemas.comment import CommentCreate, CommentResponse
from app.api.deps import get_current_active_user
from app.core.enums import UserRole
from app.services.comment_service import create_comment, list_ticket_comments
from app.services.ticket_service import get_ticket, can_user_access_ticket
from app.i18n.translator import translate
from app.i18n.fastapi_utils import resolve_lang

router = APIRouter()


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
  request: Request,
  data: CommentCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_active_user)
):
  ticket = get_ticket(db, data.ticket_id)
  if not ticket:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("tickets.not_found", resolve_lang(request, current_user)))
  if not can_user_access_ticket(current_user, ticket):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=translate("common.forbidden", resolve_lang(request, current_user)))
  if data.is_internal and current_user.role not in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.BRANCH_ADMIN):
    # only admin-level roles can add internal notes
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=translate("common.forbidden", resolve_lang(request, current_user)))
  return create_comment(db, current_user.id, data)


@router.get("/ticket/{ticket_id}", response_model=List[CommentResponse])
async def list_comments(
  request: Request,
  ticket_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_active_user)
):
  ticket = get_ticket(db, ticket_id)
  if not ticket:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=translate("tickets.not_found", resolve_lang(request, current_user)))
  if not can_user_access_ticket(current_user, ticket):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=translate("common.forbidden", resolve_lang(request, current_user)))
  include_internal = current_user.role in (UserRole.ADMIN, UserRole.CENTRAL_ADMIN, UserRole.BRANCH_ADMIN)
  return list_ticket_comments(db, ticket_id, include_internal=include_internal)

