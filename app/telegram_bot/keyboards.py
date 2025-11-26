"""
Inline keyboards used by the Telegram bot.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

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


__all__ = [
    "main_menu_keyboard",
    "category_keyboard",
    "branch_keyboard",
    "language_keyboard",
    "skip_attachments_keyboard",
    "finish_attachments_keyboard",
    "status_keyboard",
]

