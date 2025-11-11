"""
Conversation state definitions for Telegram bot flows.
"""
from enum import Enum, auto


class LoginState(Enum):
    USERNAME = auto()
    PASSWORD = auto()


class TicketState(Enum):
    TITLE = auto()
    DESCRIPTION = auto()
    CATEGORY = auto()
    ATTACHMENTS = auto()


class TrackState(Enum):
    NUMBER = auto()


__all__ = ["LoginState", "TicketState", "TrackState"]

