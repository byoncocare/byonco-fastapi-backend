"""
Pydantic models for Authentication
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, description="Full name is required")
    phone: str = Field(..., min_length=10, description="Phone number is required")
    agree_to_terms: bool = Field(..., description="Must agree to terms and conditions")


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Google OAuth token request"""
    id_token: str = Field(..., description="Google ID token from client")
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    email: str
    full_name: str
    phone: str
    is_verified: bool
    created_at: datetime
    auth_provider: str  # "email" or "google"
    # Profile fields
    profile_completed: Optional[bool] = False
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    photo_url: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class ProfileUpdate(BaseModel):
    """Profile update request"""
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)







