"""
Enums for the application
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    CENTRAL_ADMIN = "central_admin"
    ADMIN = "admin"
    BRANCH_ADMIN = "branch_admin"
    IT_SPECIALIST = "it_specialist"
    REPORT_MANAGER = "report_manager"
    USER = "user"


class Language(str, Enum):
    """Supported languages"""
    FA = "fa"  # Persian
    EN = "en"  # English


class TicketCategory(str, Enum):
    """Ticket categories"""
    INTERNET = "internet"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    OTHER = "other"


class TicketStatus(str, Enum):
    """Ticket statuses"""
    PENDING = "pending"           # در انتظار
    IN_PROGRESS = "in_progress"   # در حال بررسی
    RESOLVED = "resolved"         # حل شده
    CLOSED = "closed"             # بسته شده


class TicketPriority(str, Enum):
    """Ticket priorities"""
    CRITICAL = "critical"         # بحرانی
    HIGH = "high"                 # بالا
    MEDIUM = "medium"             # متوسط
    LOW = "low"                   # پایین

