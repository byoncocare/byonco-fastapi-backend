"""
Shared Pydantic models and helper functions
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

# Import seed data for helper functions
from app.data.seed_data import (
    HOSPITALS,
    DOCTORS,
    ALL_CANCERS,
    RARE_CANCERS,
    COMMON_CANCERS,
    CITIES,
)


# ======================================
# MODELS
# ======================================

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class PatientMatchRequest(BaseModel):
    cancer_type: Optional[str] = None
    city: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    insurance: Optional[str] = None
    preferred_language: Optional[str] = None
    treatment_type: Optional[str] = None
    international_patient: Optional[bool] = False


class PatientMatchResponse(BaseModel):
    hospitals: List[Dict[str, Any]]
    doctors: List[Dict[str, Any]]
    match_score: float
    ai_recommendation: str


class SecondOpinionRequest(BaseModel):
    patient_name: str
    cancer_type: str
    current_diagnosis: str
    current_treatment: Optional[str] = None
    medical_history: Optional[str] = None
    questions: Optional[str] = None


class SecondOpinionResponse(BaseModel):
    id: str
    patient_name: str
    status: str
    estimated_time: str
    created_at: datetime


class AppointmentRequest(BaseModel):
    patient_name: str
    patient_email: str
    patient_phone: str
    hospital_id: Optional[str] = None  # Optional for teleconsultation
    doctor_id: Optional[str] = None
    doctor_type: Optional[str] = None  # New field for doctor type selection
    appointment_type: str
    preferred_date: Optional[str] = None
    cancer_type: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    patient_name: str
    hospital_name: str
    appointment_type: str
    status: str
    created_at: datetime


class ContactRequest(BaseModel):
    name: str
    email: str
    phone: str
    message: str


class ContactResponse(BaseModel):
    id: str
    message: str
    status: str


# ======================================
# HELPER FUNCTIONS
# ======================================

def filter_hospitals(
    city: Optional[str] = None,
    cancer_type: Optional[str] = None,
    budget_max: Optional[int] = None,
    insurance: Optional[str] = None,
    international_patient: Optional[bool] = False,
) -> List[Dict[str, Any]]:
    results = []
    cities_to_search = [city] if city else CITIES

    for search_city in cities_to_search:
        if search_city not in HOSPITALS:
            continue

        for hospital in HOSPITALS[search_city]:
            if cancer_type and cancer_type not in hospital["specializations"]:
                continue
            if budget_max and hospital["cost_range"]["min"] > budget_max:
                continue
            if insurance and insurance not in hospital.get("insurance_types", []):
                continue
            if international_patient and not hospital.get("international_patients", False):
                continue

            results.append(hospital)

    results.sort(
        key=lambda x: (x["success_rate"], x["beds_available"]), reverse=True
    )
    return results


def filter_doctors(
    city: Optional[str] = None, hospital_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    results = []

    for doctor in DOCTORS:
        if city and doctor["city"] != city:
            continue
        if hospital_ids and doctor["hospital_id"] not in hospital_ids:
            continue
        results.append(doctor)

    results.sort(key=lambda x: (x["rating"], x["experience"]), reverse=True)
    return results


async def get_ai_recommendation(
    cancer_type: Optional[str],
    city: Optional[str],
    budget_max: Optional[int],
    hospitals: List[Dict[str, Any]],
) -> str:
    """
    AI disabled for local mode.
    """
    return "AI module disabled in local mode — backend running normally."


async def analyze_medical_report(report_text: str, cancer_type: str) -> str:
    """
    AI disabled for local mode.
    """
    return "AI analysis disabled in local mode — backend running normally."
