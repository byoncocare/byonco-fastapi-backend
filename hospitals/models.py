"""
Pydantic models for Hospitals API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid


class Doctor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    specialization: str
    qualifications: str
    experience: int
    hospital_id: str


class Hospital(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    city: str
    address: str
    contact: str
    email: str
    rating: float
    total_reviews: int
    specialties: List[str]
    cancer_types: List[str]
    facilities: List[str]
    image_url: str
    established_year: int


class CancerType(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str


class City(BaseModel):
    name: str














