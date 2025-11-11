from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    ticket_id: int
    comment: str = Field(..., min_length=1)
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: Optional[int] = None
    comment: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

