"""
Business logic for Hospitals API
"""
from typing import List, Optional, Dict, Any
from .seed_data import HOSPITALS, DOCTORS
import uuid
import sys
from pathlib import Path

# Import rare cancer specialists
rare_cancers_path = Path(__file__).parent.parent / "rare_cancers"
sys.path.insert(0, str(rare_cancers_path))
try:
    from seed_data import RARE_CANCER_SPECIALISTS
except ImportError:
    RARE_CANCER_SPECIALISTS = {}


class HospitalsService:
    """Service class for hospital-related operations"""
    
    def __init__(self):
        self.hospitals = HOSPITALS
        self.doctors = DOCTORS
    
    def get_all_hospitals(
        self,
        city: Optional[str] = None,
        cancer_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all hospitals with optional filtering by city and cancer type.
        Returns array format that matches frontend expectations.
        """
        all_hospitals = []
        
        # Get hospitals from the city if specified, otherwise all cities
        cities_to_check = [city] if city and city in self.hospitals else list(self.hospitals.keys())
        
        for city_name in cities_to_check:
            for hospital in self.hospitals.get(city_name, []):
                # Convert to format expected by frontend
                hospital_data = {
                    "id": hospital.get("id", str(uuid.uuid4())),
                    "name": hospital.get("name", ""),
                    "city": hospital.get("city", city_name),
                    "address": hospital.get("address", f"{hospital.get('name', '')}, {city_name}, India"),
                    "contact": hospital.get("contact", "+91-XX-XXXX-XXXX"),
                    "email": hospital.get("email", f"info@{hospital.get('name', '').lower().replace(' ', '')}.com"),
                    "rating": hospital.get("rating", 4.5),
                    "total_reviews": hospital.get("reviews_count", 0),
                    "specialties": hospital.get("specializations", []),
                    "cancer_types": hospital.get("specializations", []),  # Using specializations as cancer types
                    "facilities": hospital.get("treatments", []),
                    "image_url": hospital.get("image_url", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800"),
                    "established_year": hospital.get("established_year", 2000)
                }
                
                # Filter by cancer_type if specified
                if cancer_type:
                    if cancer_type.lower() in [s.lower() for s in hospital_data["cancer_types"]]:
                        all_hospitals.append(hospital_data)
                else:
                    all_hospitals.append(hospital_data)
        
        return all_hospitals
    
    def get_hospital_by_id(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific hospital by ID"""
        for city_hospitals in self.hospitals.values():
            for hospital in city_hospitals:
                if hospital.get("id") == hospital_id:
                    return hospital
        return None
    
    def get_doctors_by_hospital(self, hospital_id: str) -> List[Dict[str, Any]]:
        """Get doctors for a specific hospital"""
        hospital_doctors = [
            {
                "id": doc["id"],
                "name": doc["name"],
                "specialization": doc.get("specialty", "Oncology"),
                "qualifications": "MD, DM",  # Default since not in data
                "experience": doc.get("experience", 0),
                "hospital_id": doc.get("hospital_id", hospital_id)
            }
            for doc in self.doctors
            if doc.get("hospital_id") == hospital_id
        ]
        return hospital_doctors
    
    def get_all_doctors(
        self,
        city: Optional[str] = None,
        specialty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all doctors with optional filtering - includes both general doctors and rare cancer specialists"""
        doctors = self.doctors.copy()
        
        # Add rare cancer specialists to the list
        specialist_counter = len(doctors) + 1
        for cancer_name, specialists in RARE_CANCER_SPECIALISTS.items():
            for specialist in specialists:
                # Convert specialist format to doctor format
                doctor_entry = {
                    "id": f"specialist-{specialist_counter}",
                    "name": specialist.get("name", ""),
                    "specialty": ", ".join(specialist.get("specialties", [])) if specialist.get("specialties") else specialist.get("title", "Oncology"),
                    "experience": specialist.get("experience_years", 0),
                    "city": specialist.get("city", ""),
                    "country": specialist.get("country", ""),
                    "region": specialist.get("region", ""),
                    "institution": specialist.get("institution", ""),
                    "title": specialist.get("title", ""),
                    "specialties": specialist.get("specialties", []),
                    "cancer_specialization": cancer_name,
                    "hospital_id": "",  # Specialists may not be linked to specific hospitals
                    "rating": 4.8,  # Default rating for specialists
                    "consultations": 0,
                    "is_specialist": True  # Flag to identify specialists
                }
                doctors.append(doctor_entry)
                specialist_counter += 1
        
        # Apply filters
        if city:
            doctors = [d for d in doctors if d.get("city", "").lower() == city.lower()]
        
        if specialty:
            # Check both specialty field and specialties array
            doctors = [
                d for d in doctors 
                if specialty.lower() in d.get("specialty", "").lower() 
                or any(specialty.lower() in s.lower() for s in d.get("specialties", []))
            ]
        
        return doctors
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific doctor by ID"""
        for doctor in self.doctors:
            if doctor.get("id") == doctor_id:
                return doctor
        return None

