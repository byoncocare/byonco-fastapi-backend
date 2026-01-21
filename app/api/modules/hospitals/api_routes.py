"""
API routes for Hospitals feature
"""
from fastapi import APIRouter, HTTPException, Query
from .models import Hospital, Doctor
from .service import HospitalsService
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


def create_api_router():
    """
    Create and return the API router for hospitals.
    Similar structure to cost_calculator/api_routes.py
    """
    router = APIRouter(prefix="/api", tags=["hospitals"])
    service = HospitalsService()
    
    @router.get("/hospitals")
    async def get_all_hospitals(
        city: Optional[str] = Query(None, description="Filter by city"),
        cancer_type: Optional[str] = Query(None, description="Filter by cancer type")
    ):
        """Get all hospitals with optional filtering"""
        try:
            hospitals = service.get_all_hospitals(city=city, cancer_type=cancer_type)
            # Ensure email field exists for all hospitals (required by frontend)
            for h in hospitals:
                if not h.get("email") and h.get("contactEmail"):
                    h["email"] = h["contactEmail"].split(",")[0].strip() if h["contactEmail"] else ""
                elif not h.get("email"):
                    h["email"] = f"info@{h.get('name', '').lower().replace(' ', '')}.com"
            return hospitals
        except Exception as e:
            logger.error(f"Error fetching hospitals: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to fetch hospitals: {str(e)}")
    
    @router.get("/hospitals/{hospital_id}", response_model=Hospital)
    async def get_hospital(hospital_id: str):
        """Get a specific hospital by ID"""
        try:
            hospital = service.get_hospital_by_id(hospital_id)
            if not hospital:
                raise HTTPException(status_code=404, detail="Hospital not found")
            
            # Convert to frontend format
            return {
                "id": hospital.get("id", str(uuid.uuid4())),
                "name": hospital.get("name", ""),
                "city": hospital.get("city", ""),
                "address": hospital.get("address", f"{hospital.get('name', '')}, {hospital.get('city', '')}, India"),
                "contact": hospital.get("contact", "+91-XX-XXXX-XXXX"),
                "email": hospital.get("email", f"info@{hospital.get('name', '').lower().replace(' ', '')}.com"),
                "rating": hospital.get("rating", 4.5),
                "total_reviews": hospital.get("reviews_count", 0),
                "specialties": hospital.get("specializations", []),
                "cancer_types": hospital.get("specializations", []),
                "facilities": hospital.get("treatments", []),
                "image_url": hospital.get("image_url", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800"),
                "established_year": hospital.get("established_year", 2000)
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching hospital: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch hospital")
    
    @router.get("/hospitals/{hospital_id}/doctors", response_model=List[Doctor])
    async def get_doctors_by_hospital(hospital_id: str):
        """Get doctors for a specific hospital"""
        try:
            doctors = service.get_doctors_by_hospital(hospital_id)
            return doctors
        except Exception as e:
            logger.error(f"Error fetching doctors: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch doctors")
    
    @router.get("/doctors", response_model=List[Doctor])
    async def get_all_doctors(
        city: Optional[str] = Query(None, description="Filter by city"),
        specialty: Optional[str] = Query(None, description="Filter by specialty")
    ):
        """Get all doctors with optional filtering - includes both general doctors and rare cancer specialists"""
        try:
            doctors = service.get_all_doctors(city=city, specialty=specialty)
            # Convert to Doctor model format
            result = []
            for doc in doctors:
                # Handle both regular doctors and specialists
                if doc.get("is_specialist"):
                    # For specialists, use title as specialization and include additional info
                    specialization = doc.get("specialty", doc.get("title", "Oncology"))
                    if doc.get("specialties"):
                        specialization = ", ".join(doc.get("specialties", []))
                else:
                    specialization = doc.get("specialty", "Oncology")
                
                result.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "specialization": specialization,
                    "qualifications": doc.get("title", "MD, DM") if doc.get("is_specialist") else "MD, DM",
                    "experience": doc.get("experience", doc.get("experience_years", 0)),
                    "hospital_id": doc.get("hospital_id", ""),
                    # Include additional fields for specialists (will be ignored by model but useful for frontend)
                    "institution": doc.get("institution", ""),
                    "city": doc.get("city", ""),
                    "country": doc.get("country", ""),
                    "region": doc.get("region", ""),
                    "cancer_specialization": doc.get("cancer_specialization", ""),
                    "is_specialist": doc.get("is_specialist", False)
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching doctors: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch doctors")
    
    @router.get("/doctors/{doctor_id}", response_model=Doctor)
    async def get_doctor(doctor_id: str):
        """Get a specific doctor by ID"""
        try:
            doctor = service.get_doctor_by_id(doctor_id)
            if not doctor:
                raise HTTPException(status_code=404, detail="Doctor not found")
            
            return {
                "id": doctor["id"],
                "name": doctor["name"],
                "specialization": doctor.get("specialty", "Oncology"),
                "qualifications": "MD, DM",
                "experience": doctor.get("experience", 0),
                "hospital_id": doctor.get("hospital_id", "")
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching doctor: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch doctor")
    
    return router
