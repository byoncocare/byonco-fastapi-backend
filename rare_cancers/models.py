"""
Pydantic models for Rare Cancers API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid


class RareCancer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # ultra-rare, very-rare, rare
    type: str  # e.g., "Pediatric Brain Tumor", "Sarcoma"
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    treatment_options: Optional[List[str]] = None
    prognosis: Optional[str] = None
    research_status: Optional[str] = None


class RareCancerDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    category: str
    type: str
    description: str
    symptoms: List[str]
    treatment_options: List[str]
    prognosis: str
    research_status: str
    specialized_centers: List[Dict[str, Any]]
    specialists: List[Dict[str, Any]]
    clinical_trials: Optional[List[Dict[str, Any]]] = None



