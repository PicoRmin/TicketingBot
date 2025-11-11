"""
Enums for the application
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    
    # برای نسخه‌های بعدی
    # CENTRAL_ADMIN = "central_admin"
    # BRANCH_ADMIN = "branch_admin"
    # REPORT_MANAGER = "report_manager"
    # STAFF = "staff"


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

