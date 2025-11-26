"""
Profile / onboarding API endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.profile import UserProfileRequest, UserProfileResponse
from app.services.profile_service import get_profile_response, update_profile, get_or_create_profile
from app.models import User

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = get_or_create_profile(db, current_user)
    return get_profile_response(profile)


@router.post("/onboarding", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def complete_onboarding(
    payload: UserProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = update_profile(db, current_user, payload)
    return get_profile_response(profile)

