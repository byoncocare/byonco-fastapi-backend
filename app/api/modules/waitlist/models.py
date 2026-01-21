"""
Pydantic models for Medical Tourism Waitlist
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class MedicalTourismWaitlistRequest(BaseModel):
    """Medical tourism waitlist submission request"""
    user_id: Optional[str] = None
    full_name: str = Field(..., min_length=2, description="Full name is required")
    email: EmailStr
    phone: str = Field(..., min_length=10, description="Phone number is required")
    city: str = Field(..., min_length=1, description="City is required")
    country: str = Field(..., min_length=1, description="Country is required")
    cancer_type: str = Field(..., min_length=1, description="Cancer type is required")
    treatment_status: str = Field(..., description="Treatment status is required")
    preferred_destinations: List[str] = Field(..., min_items=1, description="At least one destination is required")
    budget_range: str = Field(..., description="Budget range is required")
    timeline_urgency: str = Field(..., description="Timeline urgency is required")
    additional_context: Optional[str] = None


class MedicalTourismWaitlistResponse(BaseModel):
    """Medical tourism waitlist submission response"""
    id: str
    message: str
    created_at: datetime

