"""
Database models
"""
from app.models.user import User
from app.models.ticket import Ticket
from app.models.attachment import Attachment
from app.models.branch import Branch
from app.models.comment import Comment
from app.models.ticket_history import TicketHistory
from app.models.refresh_token import RefreshToken
from app.models.settings import SystemSettings
from app.models.branch_infrastructure import BranchInfrastructure
from app.models.department import Department
from app.models.sla import SLARule, SLALog
from app.models.automation_rule import AutomationRule
from app.models.time_log import TimeLog
from app.models.custom_field import CustomField, TicketCustomFieldValue, CustomFieldType
from app.models.notification import Notification
from app.models.user_profile import UserProfile
from app.models.knowledge_article import KnowledgeArticle
from app.models.telegram_session import TelegramSession

__all__ = [
    "User",
    "Ticket",
    "Branch",
    "Attachment",
    "Comment",
    "TicketHistory",
    "RefreshToken",
    "SystemSettings",
    "BranchInfrastructure",
    "Department",
    "SLARule",
    "SLALog",
    "AutomationRule",
    "TimeLog",
    "CustomField",
    "TicketCustomFieldValue",
    "CustomFieldType",
    "Notification",
    "UserProfile",
    "KnowledgeArticle",
    "TelegramSession",
]
