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
    BRANCH = auto()
    CATEGORY = auto()
    ATTACHMENTS = auto()


class TrackState(Enum):
    NUMBER = auto()


class InfrastructureState(Enum):
    ACTION = auto()
    BRANCH = auto()
    TYPE = auto()
    NAME = auto()
    DESCRIPTION = auto()
    METADATA = auto()
    UPDATE_ID = auto()
    CONFIRM = auto()


class ChangeStatusState(Enum):
    TICKET_NUMBER = auto()
    STATUS = auto()


class ReplyState(Enum):
    TICKET_NUMBER = auto()
    COMMENT = auto()
    ATTACHMENT = auto()


class PriorityState(Enum):
    TICKET_NUMBER = auto()
    PRIORITY = auto()


class AssignState(Enum):
    TICKET_NUMBER = auto()
    USER = auto()


class SearchState(Enum):
    FILTER = auto()
    RESULTS = auto()


class BulkActionState(Enum):
    ACTION = auto()
    TICKET_SELECTION = auto()
    CONFIRM = auto()


class AlertsState(Enum):
    FILTER = auto()
    RESULTS = auto()


class SLAReportState(Enum):
    TYPE = auto()


__all__ = [
    "LoginState",
    "TicketState",
    "TrackState",
    "ChangeStatusState",
    "InfrastructureState",
    "ReplyState",
    "PriorityState",
    "AssignState",
    "SearchState",
    "BulkActionState",
    "AlertsState",
    "SLAReportState",
]

