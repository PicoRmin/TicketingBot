"""
Service helpers for onboarding profile data
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, UserProfile
from app.schemas.profile import UserProfileRequest


def get_or_create_profile(db: Session, user: User) -> UserProfile:
    if user.profile:
        return user.profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_profile_response(profile: Optional[UserProfile]):
    from app.schemas.profile import UserProfileResponse
    if not profile:
        return UserProfileResponse(
            completed=False,
            first_name=None,
            last_name=None,
            phone=None,
            age_range=None,
            skill_level=None,
            goals=[],
            responsibilities=None,
            preferred_habits=[],
            notes=None,
            completed_at=None,
            updated_at=None,
        )
    return UserProfileResponse(
        completed=profile.completed,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone=profile.phone,
        age_range=profile.age_range,
        skill_level=profile.skill_level,
        goals=profile.goals or [],
        responsibilities=profile.responsibilities,
        preferred_habits=profile.preferred_habits or [],
        notes=profile.notes,
        completed_at=profile.completed_at,
        updated_at=profile.updated_at,
    )


def update_profile(db: Session, user: User, data: UserProfileRequest) -> UserProfile:
    profile = get_or_create_profile(db, user)
    profile.first_name = data.first_name or profile.first_name
    profile.last_name = data.last_name or profile.last_name
    profile.phone = data.phone or profile.phone
    profile.age_range = data.age_range or profile.age_range
    profile.skill_level = data.skill_level or profile.skill_level
    profile.goals = data.goals or []
    profile.responsibilities = data.responsibilities
    profile.preferred_habits = data.preferred_habits or []
    profile.notes = data.notes
    profile.completed = True
    profile.completed_at = profile.completed_at or datetime.utcnow()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

