"""
Main API router for v1 endpoints
Contains core API endpoints that are not part of feature modules
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
import logging
from datetime import datetime, timezone

from app.core.models import (
    StatusCheck,
    StatusCheckCreate,
    PatientMatchRequest,
    PatientMatchResponse,
    SecondOpinionRequest,
    SecondOpinionResponse,
    AppointmentRequest,
    AppointmentResponse,
    ContactRequest,
    ContactResponse,
    filter_hospitals,
    filter_doctors,
    get_ai_recommendation,
    analyze_medical_report,
)
from app.data.seed_data import (
    HOSPITALS,
    DOCTORS,
    ALL_CANCERS,
    RARE_CANCERS,
    COMMON_CANCERS,
    CITIES,
)
from app.database import db

logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "ByOnco API - AI-Powered Cancer Care Platform"}


# -------------------------
# Status
# -------------------------
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check["timestamp"], str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])
    return status_checks


# -------------------------
# Cancer Types
# -------------------------
@api_router.get("/cancer-types")
async def get_cancer_types():
    """
    Get all cancer types.
    Returns format compatible with both old and new frontend expectations.
    """
    # Format for RareCancersPage (expects {rare_cancers, common_cancers})
    rare_cancers_list = [
        {
            "id": str(uuid.uuid4()),
            "name": cancer.get("name", ""),
            "category": cancer.get("category", "rare"),
            "type": cancer.get("type", ""),
            "description": cancer.get("type", "") + " - " + cancer.get("category", "common")
        }
        for cancer in RARE_CANCERS
    ]
    
    common_cancers_list = [
        {
            "id": str(uuid.uuid4()),
            "name": cancer.get("name", ""),
            "category": cancer.get("category", "common"),
            "type": cancer.get("type", ""),
            "description": cancer.get("type", "") + " - " + cancer.get("category", "common")
        }
        for cancer in COMMON_CANCERS
    ]
    
    # Also return as flat array for FindHospitalsPage compatibility
    all_cancers_list = [
        {
            "id": str(uuid.uuid4()),
            "name": cancer.get("name", ""),
            "description": cancer.get("type", "") + " - " + cancer.get("category", "common")
        }
        for cancer in ALL_CANCERS
    ]
    
    # Return both formats for backward compatibility
    return {
        "rare_cancers": rare_cancers_list,
        "common_cancers": common_cancers_list,
        "all_cancers": all_cancers_list
    }


# -------------------------
# Cities
# -------------------------
@api_router.get("/cities")
async def get_cities():
    return {"cities": CITIES}


# -------------------------
# Hospital Matching
# -------------------------
@api_router.post("/match-hospitals")
async def match_hospitals(request: PatientMatchRequest):
    try:
        hospitals = filter_hospitals(
            city=request.city,
            cancer_type=request.cancer_type,
            budget_max=request.budget_max,
            insurance=request.insurance,
            international_patient=request.international_patient,
        )

        hospital_ids = [h["id"] for h in hospitals]
        doctors = filter_doctors(city=request.city, hospital_ids=hospital_ids)

        match_score = min(100, len(hospitals) * 10 + len(doctors) * 5)

        ai_recommendation = await get_ai_recommendation(
            request.cancer_type, request.city, request.budget_max, hospitals
        )

        return {
            "hospitals": hospitals[:10],
            "doctors": doctors[:15],
            "match_score": match_score,
            "ai_recommendation": ai_recommendation,
        }
    except Exception as e:
        logger.error(f"Hospital matching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Second Opinion
# -------------------------
@api_router.post("/second-opinion")
async def request_second_opinion(request: SecondOpinionRequest):
    try:
        opinion_id = str(uuid.uuid4())

        report_text = f"""
Cancer Type: {request.cancer_type}
Current Diagnosis: {request.current_diagnosis}
Current Treatment: {request.current_treatment or 'Not specified'}
Medical History: {request.medical_history or 'Not provided'}
Questions: {request.questions or 'None'}
"""

        ai_analysis = await analyze_medical_report(
            report_text, request.cancer_type
        )

        opinion_doc = {
            "id": opinion_id,
            "patient_name": request.patient_name,
            "cancer_type": request.cancer_type,
            "current_diagnosis": request.current_diagnosis,
            "current_treatment": request.current_treatment,
            "medical_history": request.medical_history,
            "questions": request.questions,
            "ai_analysis": ai_analysis,
            "status": "pending_review",
            "estimated_time": "12-24 hours",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.second_opinions.insert_one(opinion_doc)

        return {
            "id": opinion_id,
            "patient_name": request.patient_name,
            "status": "pending_review",
            "estimated_time": "12-24 hours",
            "ai_preliminary_analysis": ai_analysis,
            "created_at": datetime.now(timezone.utc),
        }
    except Exception as e:
        logger.error(f"Second opinion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/second-opinion/{opinion_id}")
async def get_second_opinion(opinion_id: str):
    opinion = await db.second_opinions.find_one({"id": opinion_id}, {"_id": 0})
    if not opinion:
        raise HTTPException(status_code=404, detail="Second opinion not found")
    return opinion


# -------------------------
# Appointments
# -------------------------
@api_router.post("/appointments")
async def book_appointment(request: AppointmentRequest):
    try:
        appointment_id = str(uuid.uuid4())

        hospital = None
        hospital_name = "To be assigned"
        
        # If hospital_id is provided, find the hospital
        if request.hospital_id:
            for city_hospitals in HOSPITALS.values():
                for h in city_hospitals:
                    if h["id"] == request.hospital_id:
                        hospital = h
                        hospital_name = hospital["name"]
                        break
                if hospital:
                    break

        appointment_doc = {
            "id": appointment_id,
            "patient_name": request.patient_name,
            "patient_email": request.patient_email,
            "patient_phone": request.patient_phone,
            "hospital_id": request.hospital_id,
            "hospital_name": hospital_name,
            "doctor_id": request.doctor_id,
            "doctor_type": request.doctor_type,  # Store doctor type
            "appointment_type": request.appointment_type,
            "preferred_date": request.preferred_date,
            "cancer_type": request.cancer_type,
            "notes": request.notes,
            "status": "pending_confirmation",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.appointments.insert_one(appointment_doc)

        return {
            "id": appointment_id,
            "patient_name": request.patient_name,
            "hospital_name": hospital_name,
            "doctor_type": request.doctor_type,
            "appointment_type": request.appointment_type,
            "status": "pending_confirmation",
            "message": "Your appointment request has been received. You will be contacted within 2 hours.",
            "created_at": datetime.now(timezone.utc),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Appointment booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/appointments")
async def get_appointments(patient_email: Optional[str] = None):
    query = {}
    if patient_email:
        query["patient_email"] = patient_email

    appointments = await db.appointments.find(query, {"_id": 0}).to_list(100)
    return {"appointments": appointments}


# -------------------------
# Contact Form (Free Trial / Request Demo)
# -------------------------
@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact(request: ContactRequest):
    """Handle contact form submissions from Free Trial / Request Demo buttons"""
    try:
        contact_id = str(uuid.uuid4())
        
        contact_doc = {
            "id": contact_id,
            "name": request.name,
            "email": request.email.lower(),
            "phone": request.phone,
            "message": request.message,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        await db.contacts.insert_one(contact_doc)
        
        return {
            "id": contact_id,
            "message": "Contact form submitted successfully",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Stats
# -------------------------
@api_router.get("/stats")
async def get_stats():
    total_hospitals = sum(len(city_hospitals) for city_hospitals in HOSPITALS.values())
    total_doctors = len(DOCTORS)
    
    # Count specialists from rare cancer specialists
    from app.api.modules.rare_cancers.seed_data import RARE_CANCER_SPECIALISTS
    total_specialists = sum(len(specialists) for specialists in RARE_CANCER_SPECIALISTS.values())
    
    # Total oncologists = regular doctors + specialists
    total_oncologists = total_doctors + total_specialists
    total_cancer_types = len(ALL_CANCERS)

    return {
        "hospitals_mapped": total_hospitals,
        "doctors_available": total_oncologists,  # Now includes specialists
        "cancer_types_supported": total_cancer_types,
        "cities_covered": len(CITIES),
        "rare_cancers": len(RARE_CANCERS),
        "common_cancers": len(COMMON_CANCERS),
    }
