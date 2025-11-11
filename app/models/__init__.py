"""
Database models
"""
from app.models.user import User
from app.models.ticket import Ticket
from app.models.attachment import Attachment
from app.models.branch import Branch
from app.models.comment import Comment

__all__ = ["User", "Ticket", "Attachment", "Branch", "Comment"]
