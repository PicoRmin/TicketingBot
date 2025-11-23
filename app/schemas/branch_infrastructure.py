"""
Branch Infrastructure schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BranchInfrastructureBase(BaseModel):
    """Base schema for branch infrastructure"""
    branch_id: int = Field(..., description="شناسه شعبه")
    infrastructure_type: str = Field(..., description="نوع زیرساخت (ip, server, equipment, service)")
    name: str = Field(..., min_length=1, max_length=255, description="نام")
    description: Optional[str] = Field(None, description="توضیحات")
    ip_address: Optional[str] = Field(None, max_length=50, description="آدرس IP")
    hostname: Optional[str] = Field(None, max_length=255, description="نام میزبان")
    model: Optional[str] = Field(None, max_length=255, description="مدل")
    serial_number: Optional[str] = Field(None, max_length=255, description="شماره سریال")
    service_type: Optional[str] = Field(None, max_length=100, description="نوع سرویس")
    service_url: Optional[str] = Field(None, max_length=512, description="آدرس سرویس")
    status: str = Field(default="active", description="وضعیت (active, inactive, maintenance)")
    notes: Optional[str] = Field(None, description="یادداشت‌ها")


class BranchInfrastructureCreate(BranchInfrastructureBase):
    """Schema for creating branch infrastructure"""
    pass


class BranchInfrastructureUpdate(BaseModel):
    """Schema for updating branch infrastructure"""
    branch_id: Optional[int] = None
    infrastructure_type: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=50)
    hostname: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)
    service_type: Optional[str] = Field(None, max_length=100)
    service_url: Optional[str] = Field(None, max_length=512)
    status: Optional[str] = None
    notes: Optional[str] = None


class BranchInfrastructureResponse(BranchInfrastructureBase):
    """Schema for branch infrastructure response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True

