"""
Automation Rule schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class AutomationRuleBase(BaseModel):
    """Base schema for automation rule"""
    name: str = Field(..., min_length=1, max_length=255, description="نام قانون")
    description: Optional[str] = Field(None, description="توضیحات")
    rule_type: str = Field(..., description="نوع قانون: auto_assign, auto_close, auto_notify")
    conditions: Optional[Dict[str, Any]] = Field(None, description="شرایط فعال شدن (JSON)")
    actions: Dict[str, Any] = Field(..., description="اقدامات (JSON)")
    priority: int = Field(default=100, ge=1, le=1000, description="اولویت اجرا (کمتر = اولویت بالاتر)")
    is_active: bool = Field(default=True, description="وضعیت فعال/غیرفعال")


class AutomationRuleCreate(AutomationRuleBase):
    """Schema for creating automation rule"""
    pass


class AutomationRuleUpdate(BaseModel):
    """Schema for updating automation rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None


class AutomationRuleResponse(AutomationRuleBase):
    """Schema for automation rule response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

