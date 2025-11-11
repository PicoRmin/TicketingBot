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
]
