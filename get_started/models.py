"""
Pydantic models for Get Started form submissions
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class GetStartedRequest(BaseModel):
    """Get Started form submission request"""
    # Personal Information (All Mandatory)
    full_name: str = Field(..., min_length=2, description="Full name is required")
    email: EmailStr = Field(..., description="Email is required")
    phone: str = Field(..., min_length=10, description="Phone number is required")
    
    # Location Information (All Mandatory)
    city: str = Field(..., min_length=2, description="City is required")
    state: Optional[str] = None
    country: str = Field(default="India", description="Country")
    
    # Medical Information (All Mandatory)
    cancer_type: str = Field(..., min_length=2, description="Cancer type is required")
    cancer_stage: str = Field(..., description="Cancer stage is required")
    
    # Insurance Information (All Mandatory)
    has_insurance: bool = Field(default=False, description="Insurance status")
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    
    # Additional Information
    preferred_language: str = Field(default="en", description="Preferred language")
    preferred_contact_method: str = Field(default="phone", description="Preferred contact method")
    preferred_time: Optional[str] = None
    additional_notes: Optional[str] = None
    
    # Consent
    agree_to_terms: bool = Field(..., description="Must agree to terms and conditions")
    agree_to_contact: bool = Field(default=True, description="Agreement to be contacted")


class GetStartedResponse(BaseModel):
    """Get Started form submission response"""
    id: str
    message: str
    submitted_at: datetime
    status: str = "pending_review"


class GetStartedSubmission(BaseModel):
    """Get Started submission model for database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: str
    phone: str
    city: str
    state: Optional[str] = None
    country: str
    cancer_type: str
    cancer_stage: str
    has_insurance: bool
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    preferred_language: str
    preferred_contact_method: str
    preferred_time: Optional[str] = None
    additional_notes: Optional[str] = None
    agree_to_terms: bool
    agree_to_contact: bool
    status: str = "pending_review"  # pending_review, contacted, in_progress, completed
    created_at: datetime
    updated_at: datetime







