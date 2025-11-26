"""
Pydantic schemas for user profile / onboarding
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserProfileRequest(BaseModel):
  first_name: Optional[str] = None
  last_name: Optional[str] = None
  phone: Optional[str] = None
  age_range: Optional[str] = None
  skill_level: Optional[str] = None
  goals: Optional[List[str]] = Field(default_factory=list)
  responsibilities: Optional[str] = None
  preferred_habits: Optional[List[str]] = Field(default_factory=list)
  notes: Optional[str] = None


class UserProfileResponse(BaseModel):
  completed: bool
  first_name: Optional[str]
  last_name: Optional[str]
  phone: Optional[str]
  age_range: Optional[str]
  skill_level: Optional[str]
  goals: List[str] = Field(default_factory=list)
  responsibilities: Optional[str]
  preferred_habits: List[str] = Field(default_factory=list)
  notes: Optional[str]
  completed_at: Optional[datetime]
  updated_at: Optional[datetime]

  class Config:
    orm_mode = True

