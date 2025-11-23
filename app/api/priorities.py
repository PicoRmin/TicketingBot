"""
Priorities API endpoints
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models import User
from app.schemas.priority import get_all_priorities, PriorityInfo

router = APIRouter()


@router.get("", response_model=list[PriorityInfo])
async def get_priorities(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all ticket priorities
    
    Returns:
        List of priority information
    """
    return get_all_priorities()

