from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio

# ======================================
# Load environment variables
# ======================================
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# ======================================
# MongoDB Connection
# ======================================
mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get("DB_NAME", "test_database")]

# ======================================
# FastAPI App + Router
# ======================================
app = FastAPI()

# CORS settings
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://byoncocare.com",
    "https://www.byoncocare.com",
    "https://byonco.onrender.com",
    "https://byonco-goaj7ykq-byonco-cares-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# ======================================
# LLM Config (Disabled in local mode)
# ======================================
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# ======================================
# Import Seed Data
# ======================================
# Ensure backend directory is in path for data_seed import
_backend_dir = Path(__file__).parent.absolute()
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from data_seed import (
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


# ======================================
# API ENDPOINTS
# ======================================

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
        logging.error(f"Hospital matching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Hospital List - MOVED TO hospitals/api_routes.py
# -------------------------
# These routes are now handled by the hospitals module
# Keeping this comment for reference

# -------------------------
# Doctors - MOVED TO hospitals/api_routes.py
# -------------------------
# These routes are now handled by the hospitals module
# Keeping this comment for reference


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
        logging.error(f"Second opinion error: {e}")
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
        logging.error(f"Appointment booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/appointments")
async def get_appointments(patient_email: Optional[str] = None):
    query = {}
    if patient_email:
        query["patient_email"] = patient_email

    appointments = await db.appointments.find(query, {"_id": 0}).to_list(100)
    return {"appointments": appointments}


# -------------------------
# Stats
# -------------------------
@api_router.get("/stats")
async def get_stats():
    total_hospitals = sum(len(city_hospitals) for city_hospitals in HOSPITALS.values())
    total_doctors = len(DOCTORS)
    
    # Count specialists from rare cancer specialists
    from rare_cancers.seed_data import RARE_CANCER_SPECIALISTS
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


# ======================================
# Register Router + CORS
# ======================================
# Root route
@app.get("/")
async def root():
    # Get all registered routes for debugging
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    
    return {
        "message": "ByOnco API Server",
        "version": "1.0.0",
        "endpoints": {
            "api_root": "/api",
            "hospitals": "/api/hospitals",
            "cancer_types": "/api/cancer-types",
            "cities": "/api/cities",
            "doctors": "/api/doctors"
        },
        "registered_routes": routes[:20]  # Show first 20 routes for debugging
    }

app.include_router(api_router)

# ======================================
# Cost Calculator Routes
# ======================================
cost_calculator_path = Path(__file__).parent / "cost_calculator"
sys.path.insert(0, str(cost_calculator_path))

from api_routes import create_api_router as create_cost_calculator_router
cost_calculator_router = create_cost_calculator_router(db)
app.include_router(cost_calculator_router)

# ======================================
# Hospitals Routes (Modular)
# ======================================
from hospitals.api_routes import create_api_router as create_hospitals_router
hospitals_router = create_hospitals_router()
app.include_router(hospitals_router)

# ======================================
# Rare Cancers Routes (Modular)
# ======================================
from rare_cancers.api_routes import create_api_router as create_rare_cancers_router
rare_cancers_router = create_rare_cancers_router()
app.include_router(rare_cancers_router)

# ======================================
# Authentication Routes
# ======================================
from auth.api_routes import create_api_router as create_auth_router
auth_router = create_auth_router(db)
app.include_router(auth_router)

# ======================================
# Payment Routes
# ======================================
from payments.api_routes import create_api_router as create_payments_router
payments_router = create_payments_router(db)
app.include_router(payments_router)

# ======================================
# Get Started Routes
# ======================================
from get_started.api_routes import create_api_router as create_get_started_router
get_started_router = create_get_started_router(db)
app.include_router(get_started_router)

# CORS middleware already added above after app creation

# ======================================
# Logging
# ======================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ======================================
# Shutdown Handler
# ======================================
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
