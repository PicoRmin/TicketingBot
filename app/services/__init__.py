"""
Business logic services
"""
from app.services.ticket_service import (
    generate_ticket_number,
    create_ticket,
    get_ticket,
    get_ticket_by_number,
    update_ticket,
    update_ticket_status,
    get_user_tickets,
    get_all_tickets,
    delete_ticket,
    can_user_access_ticket,
)
from app.services.file_service import (
    validate_file,
    save_file,
    create_attachment,
    get_attachment,
    get_ticket_attachments,
    delete_attachment_file,
    delete_attachment,
    can_user_access_attachment,
)
from app.services.notification_service import (
    notify_ticket_created,
    notify_ticket_status_changed,
)
from app.services.ticket_history_service import (
    create_ticket_history,
    get_ticket_history,
)
from app.services.refresh_token_service import (
    issue_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.services.user_service import (
    list_users,
    get_user,
    create_user,
    update_user,
    delete_user,
    UserServiceError,
)

__all__ = [
    # Ticket services
    "generate_ticket_number",
    "create_ticket",
    "get_ticket",
    "get_ticket_by_number",
    "update_ticket",
    "update_ticket_status",
    "get_user_tickets",
    "get_all_tickets",
    "delete_ticket",
    "can_user_access_ticket",
    # File services
    "validate_file",
    "save_file",
    "create_attachment",
    "get_attachment",
    "get_ticket_attachments",
    "delete_attachment_file",
    "delete_attachment",
    "can_user_access_attachment",
    # Notification services
    "notify_ticket_created",
    "notify_ticket_status_changed",
    "create_ticket_history",
    "get_ticket_history",
    "issue_refresh_token",
    "verify_refresh_token",
    "revoke_refresh_token",
    "rotate_refresh_token",
    "list_users",
    "get_user",
    "create_user",
    "update_user",
    "delete_user",
    "UserServiceError",
]
