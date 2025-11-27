"""
Inline keyboards used by the Telegram bot.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.enums import Language, TicketCategory, TicketStatus
from app.telegram_bot.callbacks import (
    CALLBACK_BRANCH_PREFIX,
    CALLBACK_CATEGORY_PREFIX,
    CALLBACK_CHANGE_STATUS,
    CALLBACK_HELP,
    CALLBACK_LANGUAGE,
    CALLBACK_LANGUAGE_PREFIX,
    CALLBACK_LOGIN,
    CALLBACK_LOGOUT,
    CALLBACK_MY_TICKETS,
    CALLBACK_NEW_TICKET,
    CALLBACK_SKIP_ATTACHMENTS,
    CALLBACK_FINISH_ATTACHMENTS,
    CALLBACK_TRACK_TICKET,
    CALLBACK_STATUS_PREFIX,
    CALLBACK_TICKET_REPLY,
    CALLBACK_TICKET_COMMENTS,
    CALLBACK_TICKET_HISTORY,
    CALLBACK_TICKET_ATTACHMENTS,
    CALLBACK_TICKET_PRIORITY,
    CALLBACK_TICKET_ASSIGN,
    CALLBACK_PRIORITY_PREFIX,
    CALLBACK_USER_PREFIX,
    CALLBACK_SEARCH_FILTER_STATUS,
    CALLBACK_SEARCH_FILTER_PRIORITY,
    CALLBACK_SEARCH_FILTER_CATEGORY,
    CALLBACK_SEARCH_FILTER_DATE,
    CALLBACK_BULK_SELECT,
    CALLBACK_BULK_CONFIRM,
    CALLBACK_BULK_CANCEL,
    CALLBACK_ALERTS_FILTER_WARNING,
    CALLBACK_ALERTS_FILTER_BREACH,
    CALLBACK_ALERTS_FILTER_ALL,
    CALLBACK_ALERTS_TICKET,
    CALLBACK_SLA_REPORT_COMPLIANCE,
    CALLBACK_SLA_REPORT_BY_PRIORITY,
)
from app.telegram_bot.i18n import get_message


def _button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=callback_data)


def main_menu_keyboard(language: Language, is_authenticated: bool, can_change_status: bool = False) -> InlineKeyboardMarkup:
    """Return the main menu keyboard."""
    buttons: List[List[InlineKeyboardButton]] = [
        [
            _button(get_message("menu_new_ticket", language), CALLBACK_NEW_TICKET),
            _button(get_message("menu_my_tickets", language), CALLBACK_MY_TICKETS),
        ],
        [
            _button(get_message("menu_track_ticket", language), CALLBACK_TRACK_TICKET),
            _button(get_message("menu_help", language), CALLBACK_HELP),
        ],
    ]
    
    # Add change status button for authorized users
    if can_change_status:
        buttons.append([
            _button(get_message("menu_change_status", language), CALLBACK_CHANGE_STATUS),
        ])
    
    buttons.append([
        _button(get_message("menu_language", language), CALLBACK_LANGUAGE),
    ])

    auth_button = (
        _button(get_message("menu_logout", language), CALLBACK_LOGOUT)
        if is_authenticated
        else _button(get_message("menu_login", language), CALLBACK_LOGIN)
    )
    buttons.append([auth_button])

    return InlineKeyboardMarkup(buttons)


def category_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting ticket categories."""
    categories: Iterable[TicketCategory] = (
        TicketCategory.INTERNET,
        TicketCategory.EQUIPMENT,
        TicketCategory.SOFTWARE,
        TicketCategory.OTHER,
    )

    buttons = [
        [
            _button(
                get_message(f"category_{category.value}", language),
                f"{CALLBACK_CATEGORY_PREFIX}{category.value}",
            )
        ]
        for category in categories
    ]
    return InlineKeyboardMarkup(buttons)


def language_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return language selection keyboard."""
    buttons = [
        [
            _button(
                get_message("language_name_fa", language),
                f"{CALLBACK_LANGUAGE_PREFIX}{Language.FA.value}",
            )
        ],
        [
            _button(
                get_message("language_name_en", language),
                f"{CALLBACK_LANGUAGE_PREFIX}{Language.EN.value}",
            )
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def branch_keyboard(branches: List[Dict[str, Any]], language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting branches."""
    buttons = [
        [
            _button(
                branch.get("name", f"Branch {branch.get('id')}"),
                f"{CALLBACK_BRANCH_PREFIX}{branch.get('id')}",
            )
        ]
        for branch in branches
    ]
    # Add skip option
    buttons.append([
        _button(
            get_message("branch_skip", language),
            f"{CALLBACK_BRANCH_PREFIX}skip",
        )
    ])
    return InlineKeyboardMarkup(buttons)


def skip_attachments_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Keyboard for skipping attachment upload."""
    return InlineKeyboardMarkup(
        [
            [
                _button(
                    get_message("attachments_skip_button", language),
                    CALLBACK_SKIP_ATTACHMENTS,
                )
            ]
        ]
    )


def finish_attachments_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Keyboard for finishing attachment upload (shown after each upload)."""
    return InlineKeyboardMarkup(
        [
            [
                _button(
                    get_message("attachments_finish_button", language),
                    CALLBACK_FINISH_ATTACHMENTS,
                )
            ],
            [
                _button(
                    get_message("attachments_skip_button", language),
                    CALLBACK_SKIP_ATTACHMENTS,
                )
            ]
        ]
    )


def status_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting ticket status."""
    statuses = [
        TicketStatus.PENDING,
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    ]

    buttons = [
        [
            _button(
                get_message(f"status_{status.value}", language),
                f"{CALLBACK_STATUS_PREFIX}{status.value}",
            )
        ]
        for status in statuses
    ]
    return InlineKeyboardMarkup(buttons)


def ticket_detail_keyboard(ticket_id: int, language: Language, is_manager: bool = False) -> InlineKeyboardMarkup:
    """Return a keyboard for ticket detail actions."""
    buttons: List[List[InlineKeyboardButton]] = [
        [
            _button(
                get_message("ticket_detail_reply", language),
                f"{CALLBACK_TICKET_REPLY}{ticket_id}",
            ),
            _button(
                get_message("ticket_detail_comments", language),
                f"{CALLBACK_TICKET_COMMENTS}{ticket_id}",
            ),
        ],
        [
            _button(
                get_message("ticket_detail_history", language),
                f"{CALLBACK_TICKET_HISTORY}{ticket_id}",
            ),
            _button(
                get_message("ticket_detail_attachments", language),
                f"{CALLBACK_TICKET_ATTACHMENTS}{ticket_id}",
            ),
        ],
    ]
    
    # Add manager-only actions
    if is_manager:
        buttons.append([
            _button(
                get_message("ticket_detail_priority", language),
                f"{CALLBACK_TICKET_PRIORITY}{ticket_id}",
            ),
            _button(
                get_message("ticket_detail_assign", language),
                f"{CALLBACK_TICKET_ASSIGN}{ticket_id}",
            ),
        ])
    
    return InlineKeyboardMarkup(buttons)


def priority_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting ticket priority."""
    from app.core.enums import TicketPriority
    
    priorities = [
        TicketPriority.CRITICAL,
        TicketPriority.HIGH,
        TicketPriority.MEDIUM,
        TicketPriority.LOW,
    ]
    
    buttons = [
        [
            _button(
                get_message(f"priority_{priority.value}", language),
                f"{CALLBACK_PRIORITY_PREFIX}{priority.value}",
            )
        ]
        for priority in priorities
    ]
    return InlineKeyboardMarkup(buttons)


def user_selection_keyboard(users: List[Dict[str, Any]], language: Language, callback_prefix: str = CALLBACK_USER_PREFIX) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting a user/agent."""
    buttons = []
    for user in users[:20]:  # Limit to 20 users to avoid keyboard size issues
        user_name = user.get("full_name") or user.get("username", f"User {user.get('id')}")
        buttons.append([
            _button(
                user_name,
                f"{callback_prefix}{user.get('id')}",
            )
        ])
    
    if not buttons:
        # Return empty keyboard if no users
        buttons = [[_button(get_message("assign_no_users", language), "no_users")]]
    
    return InlineKeyboardMarkup(buttons)


def internal_comment_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for selecting internal/external comment."""
    buttons = [
        [
            _button(
                get_message("comment_internal_yes", language),
                "comment_internal_yes",
            ),
            _button(
                get_message("comment_internal_no", language),
                "comment_internal_no",
            ),
        ],
        [
            _button(
                get_message("comment_skip_internal", language),
                "comment_skip_internal",
            ),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def search_filter_keyboard(language: Language, active_filters: Optional[Dict[str, Any]] = None) -> InlineKeyboardMarkup:
    """Return a keyboard for search filter selection."""
    if active_filters is None:
        active_filters = {}
    
    buttons = [
        [
            _button(
                get_message("search_filter_status", language),
                "search_status",
            ),
            _button(
                get_message("search_filter_priority", language),
                "search_priority",
            ),
        ],
        [
            _button(
                get_message("search_filter_category", language),
                "search_category",
            ),
            _button(
                get_message("search_filter_date", language),
                "search_date",
            ),
        ],
        [
            _button(
                get_message("search_text", language),
                "search_text",
            ),
        ],
    ]
    
    # Add execute and reset buttons if filters are active
    if active_filters:
        buttons.append([
            _button(
                get_message("search_execute", language),
                "search_execute",
            ),
            _button(
                get_message("search_reset", language),
                "search_reset",
            ),
        ])
    
    return InlineKeyboardMarkup(buttons)


def date_filter_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Return a keyboard for date filter selection."""
    buttons = [
        [
            _button(
                get_message("search_date_today", language),
                f"{CALLBACK_SEARCH_FILTER_DATE}today",
            ),
        ],
        [
            _button(
                get_message("search_date_week", language),
                f"{CALLBACK_SEARCH_FILTER_DATE}week",
            ),
        ],
        [
            _button(
                get_message("search_date_month", language),
                f"{CALLBACK_SEARCH_FILTER_DATE}month",
            ),
        ],
        [
            _button(
                get_message("search_date_all", language),
                f"{CALLBACK_SEARCH_FILTER_DATE}all",
            ),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def bulk_action_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Keyboard for selecting bulk action type"""
    buttons: List[List[InlineKeyboardButton]] = [
        [
            _button(get_message("bulk_action_status", language), "bulk_status"),
            _button(get_message("bulk_action_assign", language), "bulk_assign"),
        ],
        [
            _button(get_message("bulk_action_unassign", language), "bulk_unassign"),
            _button(get_message("bulk_action_delete", language), "bulk_delete"),
        ],
        [
            _button(get_message("cancel", language), CALLBACK_BULK_CANCEL),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def bulk_ticket_selection_keyboard(
    tickets: List[Dict[str, Any]],
    selected_tickets: set,
    language: Language
) -> InlineKeyboardMarkup:
    """Keyboard for selecting tickets in bulk action"""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # Add ticket buttons (max 20 tickets per page)
    for ticket in tickets[:20]:
        ticket_id = ticket.get("id")
        ticket_number = ticket.get("ticket_number", f"T-{ticket_id}")
        title = ticket.get("title", "")[:30]  # Limit title length
        
        # Check if selected
        is_selected = ticket_id in selected_tickets
        prefix = "✅ " if is_selected else "☐ "
        
        button_text = f"{prefix}{ticket_number}: {title}"
        callback_data = f"{CALLBACK_BULK_SELECT}{ticket_id}"
        
        buttons.append([_button(button_text, callback_data)])
    
    # Add action buttons
    if selected_tickets:
        buttons.append([
            _button(get_message("bulk_confirm_button", language), CALLBACK_BULK_CONFIRM),
        ])
    
    buttons.append([
        _button(get_message("cancel", language), CALLBACK_BULK_CANCEL),
    ])
    
    return InlineKeyboardMarkup(buttons)


def sla_alerts_filter_keyboard(language: Language, current_filter: str = "all") -> InlineKeyboardMarkup:
    """Keyboard for filtering SLA alerts"""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # Filter buttons
    filter_buttons = []
    
    # All button
    all_text = get_message("alerts_filter_all", language)
    if current_filter == "all":
        all_text = f"✅ {all_text}"
    filter_buttons.append(_button(all_text, CALLBACK_ALERTS_FILTER_ALL))
    
    # Warning button
    warning_text = get_message("alerts_filter_warning", language)
    if current_filter == "warning":
        warning_text = f"✅ {warning_text}"
    filter_buttons.append(_button(warning_text, CALLBACK_ALERTS_FILTER_WARNING))
    
    buttons.append(filter_buttons)
    
    # Breach button
    breach_text = get_message("alerts_filter_breach", language)
    if current_filter == "breach":
        breach_text = f"✅ {breach_text}"
    buttons.append([_button(breach_text, CALLBACK_ALERTS_FILTER_BREACH)])
    
    # Cancel button
    buttons.append([_button(get_message("cancel", language), CALLBACK_BULK_CANCEL)])
    
    return InlineKeyboardMarkup(buttons)


def sla_alerts_results_keyboard(
    alerts: List[Dict[str, Any]],
    language: Language,
    current_filter: str = "all"
) -> InlineKeyboardMarkup:
    """Keyboard for SLA alerts results"""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # Add ticket buttons (max 10 tickets per page)
    for alert in alerts[:10]:
        ticket_id = alert.get("ticket_id")
        ticket_number = alert.get("ticket_number", f"T-{ticket_id}")
        response_status = alert.get("response_status", "")
        resolution_status = alert.get("resolution_status", "")
        
        # Determine alert type
        if "breached" in [response_status.lower(), resolution_status.lower()]:
            emoji = "🔴"
        elif "warning" in [response_status.lower(), resolution_status.lower()]:
            emoji = "🟡"
        else:
            emoji = "⚪"
        
        button_text = f"{emoji} {ticket_number}"
        callback_data = f"{CALLBACK_ALERTS_TICKET}{ticket_id}"
        
        buttons.append([_button(button_text, callback_data)])
    
    # Add filter buttons
    filter_buttons = []
    
    all_text = get_message("alerts_filter_all", language)
    if current_filter == "all":
        all_text = f"✅ {all_text}"
    filter_buttons.append(_button(all_text, CALLBACK_ALERTS_FILTER_ALL))
    
    warning_text = get_message("alerts_filter_warning", language)
    if current_filter == "warning":
        warning_text = f"✅ {warning_text}"
    filter_buttons.append(_button(warning_text, CALLBACK_ALERTS_FILTER_WARNING))
    
    buttons.append(filter_buttons)
    
    breach_text = get_message("alerts_filter_breach", language)
    if current_filter == "breach":
        breach_text = f"✅ {breach_text}"
    buttons.append([_button(breach_text, CALLBACK_ALERTS_FILTER_BREACH)])
    
    # Cancel button
    buttons.append([_button(get_message("cancel", language), CALLBACK_BULK_CANCEL)])
    
    return InlineKeyboardMarkup(buttons)


def sla_report_type_keyboard(language: Language) -> InlineKeyboardMarkup:
    """Keyboard for selecting SLA report type"""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # Compliance report button
    compliance_text = get_message("sla_report_type_compliance", language)
    buttons.append([_button(compliance_text, CALLBACK_SLA_REPORT_COMPLIANCE)])
    
    # By priority report button
    priority_text = get_message("sla_report_type_by_priority", language)
    buttons.append([_button(priority_text, CALLBACK_SLA_REPORT_BY_PRIORITY)])
    
    # Cancel button
    buttons.append([_button(get_message("cancel", language), CALLBACK_BULK_CANCEL)])
    
    return InlineKeyboardMarkup(buttons)


__all__ = [
    "main_menu_keyboard",
    "category_keyboard",
    "branch_keyboard",
    "language_keyboard",
    "skip_attachments_keyboard",
    "finish_attachments_keyboard",
    "status_keyboard",
    "ticket_detail_keyboard",
    "priority_keyboard",
    "user_selection_keyboard",
    "internal_comment_keyboard",
    "search_filter_keyboard",
    "date_filter_keyboard",
    "bulk_action_keyboard",
    "bulk_ticket_selection_keyboard",
    "sla_alerts_filter_keyboard",
    "sla_alerts_results_keyboard",
    "sla_report_type_keyboard",
]

