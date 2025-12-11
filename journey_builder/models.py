"""
Pydantic models for Journey Builder
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class JourneyRequest(BaseModel):
    """Request model for journey builder"""
    message: str = Field(..., min_length=1, description="User's journey planning request")


class JourneyProfile(BaseModel):
    """Extracted journey profile from user message"""
    cancerType: Optional[str] = None
    stage: Optional[str] = None
    originDest: Optional[str] = None
    estBudget: Optional[str] = None


class JourneyPlan(BaseModel):
    """Journey plan details"""
    planType: str  # "Value", "Balanced", or "Comfort"
    city: str
    region: str
    priceRange: str
    duration: str
    hospitalName: str
    hospitalNote: str
    bullets: List[str]  # List of inclusions/features
    fitNote: str  # Why this plan fits
    overBudget: Optional[bool] = False
    icon: Optional[str] = None  # Icon identifier (e.g., "lucide:train-front")


class SuggestionItem(BaseModel):
    """Individual suggestion item"""
    title: str
    text: str


class Suggestions(BaseModel):
    """Suggestions to optimize the journey"""
    items: List[SuggestionItem]


class JourneyResponse(BaseModel):
    """Response model for journey builder"""
    profile: JourneyProfile
    plans: List[JourneyPlan]
    suggestions: Optional[Suggestions] = None
    disclaimer: Optional[str] = None

