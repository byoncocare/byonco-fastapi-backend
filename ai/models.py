"""
AI API Models for ByOnco
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class BuilderRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for treatment plan generation")
    city: Optional[str] = Field(None, description="Preferred city for treatment")
    budget_max: Optional[int] = Field(None, description="Maximum budget in INR")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional user context")


class BuilderResponse(BaseModel):
    answer: str = Field(..., description="AI-generated treatment plans as JSON string")
    model: str = Field(default="gpt-4", description="AI model used")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")


class SecondOpinionRequest(BaseModel):
    question: Optional[str] = Field(None, description="Patient's question")
    attachments: Optional[List[str]] = Field(None, description="URLs of uploaded medical reports")
    profile: Optional[Dict[str, Any]] = Field(None, description="Patient profile information")


class SecondOpinionResponse(BaseModel):
    answer: Optional[str] = Field(None, description="AI-generated second opinion analysis")
    safe: bool = Field(default=True, description="Whether the question passed medical-only validation")
    paywall_required: Optional[bool] = Field(None, description="Whether payment is required (daily limit exceeded)")
    amount_inr: Optional[int] = Field(None, description="Amount in INR if paywall is required")
    error: Optional[str] = Field(None, description="Error message if request failed")


