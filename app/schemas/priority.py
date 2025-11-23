"""
Priority schemas
"""
from pydantic import BaseModel
from app.core.enums import TicketPriority


class PriorityInfo(BaseModel):
    """Priority information"""
    value: TicketPriority
    label_fa: str
    label_en: str
    color: str
    order: int


# Priority definitions
PRIORITY_INFO = {
    TicketPriority.CRITICAL: PriorityInfo(
        value=TicketPriority.CRITICAL,
        label_fa="🔴 بحرانی",
        label_en="🔴 Critical",
        color="#dc2626",
        order=1
    ),
    TicketPriority.HIGH: PriorityInfo(
        value=TicketPriority.HIGH,
        label_fa="🟠 بالا",
        label_en="🟠 High",
        color="#f59e0b",
        order=2
    ),
    TicketPriority.MEDIUM: PriorityInfo(
        value=TicketPriority.MEDIUM,
        label_fa="🟡 متوسط",
        label_en="🟡 Medium",
        color="#eab308",
        order=3
    ),
    TicketPriority.LOW: PriorityInfo(
        value=TicketPriority.LOW,
        label_fa="🟢 پایین",
        label_en="🟢 Low",
        color="#10b981",
        order=4
    ),
}


def get_priority_info(priority: TicketPriority) -> PriorityInfo:
    """Get priority information"""
    return PRIORITY_INFO.get(priority, PRIORITY_INFO[TicketPriority.MEDIUM])


def get_all_priorities() -> list[PriorityInfo]:
    """Get all priority information sorted by order"""
    return sorted(PRIORITY_INFO.values(), key=lambda x: x.order)

