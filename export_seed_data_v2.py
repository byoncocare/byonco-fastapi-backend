"""
Export seed data from data_seed.py to JSON files for Supabase seeding.
VERSION 2: Handles UUID generation and hospital_id mapping correctly.
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

# Import the seed data
from data_seed import HOSPITALS, DOCTORS, CITIES, ALL_CANCERS, RARE_CANCERS, COMMON_CANCERS

# Also import specialists if available
try:
    from rare_cancers.seed_data import RARE_CANCER_SPECIALISTS, COMMON_CANCER_SPECIALISTS
except ImportError:
    RARE_CANCER_SPECIALISTS = {}
    COMMON_CANCER_SPECIALISTS = {}

# Output directory
OUTPUT_DIR = Path(__file__).parent / "seed_exports"
OUTPUT_DIR.mkdir(exist_ok=True)

def export_hospitals() -> tuple[List[Dict], Dict[str, str]]:
    """
    Export hospitals data, flattening the city-keyed dict into a list.
    Returns: (hospitals_list, id_mapping) where id_mapping maps original_id -> new_uuid
    """
    hospitals_list = []
    id_mapping = {}  # original_id -> generated_uuid
    
    for city, city_hospitals in HOSPITALS.items():
        for hospital in city_hospitals:
            original_id = hospital.get("id", str(uuid.uuid4()))
            # Generate UUID for this hospital
            hospital_uuid = str(uuid.uuid4())
            id_mapping[original_id] = hospital_uuid
            
            hospital_row = {
                "id": hospital_uuid,  # Use generated UUID
                "external_ref": original_id,  # Store original ID for reference
                "name": hospital.get("name", ""),
                "city": hospital.get("city", city),
                "address": hospital.get("address", ""),
                "min_estimated_cost": hospital.get("cost_range", {}).get("min"),
                "rating": float(hospital.get("rating", 0)) if hospital.get("rating") else None,
                "phone": hospital.get("phone"),
                "is_active": True,
            }
            
            # Extract phone if it's in a contact field
            if not hospital_row["phone"] and "contact" in hospital:
                hospital_row["phone"] = hospital["contact"]
            
            # Remove None values (except rating which can be None)
            hospital_row = {k: v for k, v in hospital_row.items() if v is not None or k == "rating"}
            
            hospitals_list.append(hospital_row)
    
    return hospitals_list, id_mapping

def export_doctors(hospital_id_mapping: Dict[str, str]) -> List[Dict]:
    """Export doctors data, including specialists, with proper hospital_id UUID mapping."""
    doctors_list = []
    
    # Regular doctors from DOCTORS list
    for doctor in DOCTORS:
        original_hospital_id = doctor.get("hospital_id")
        # Map to UUID if available
        hospital_uuid = hospital_id_mapping.get(original_hospital_id) if original_hospital_id else None
        
        doctor_row = {
            "id": str(uuid.uuid4()),  # Generate UUID
            "name": doctor.get("name", ""),
            "department": doctor.get("specialty", "Oncology"),
            "consultation_fee": None,  # Not in seed data
            "rating": float(doctor.get("rating", 0)) if doctor.get("rating") else None,
            "hospital_id": hospital_uuid,  # Use mapped UUID
        }
        
        # Remove None values (except rating and hospital_id which can be None)
        doctor_row = {k: v for k, v in doctor_row.items() if v is not None or k in ("rating", "hospital_id")}
        doctors_list.append(doctor_row)
    
    # Add specialists from RARE_CANCER_SPECIALISTS and COMMON_CANCER_SPECIALISTS
    all_specialists = {**RARE_CANCER_SPECIALISTS, **COMMON_CANCER_SPECIALISTS}
    
    specialist_counter = len(doctors_list) + 1
    for cancer_name, specialists in all_specialists.items():
        for specialist in specialists:
            # Try to find hospital_id by matching city/institution
            hospital_uuid = None
            specialist_city = specialist.get("city", "")
            specialist_institution = specialist.get("institution", "")
            
            # Try to match with hospitals using the mapping
            for original_id, uuid_val in hospital_id_mapping.items():
                # Find hospital by original_id
                for city, city_hospitals in HOSPITALS.items():
                    for hosp in city_hospitals:
                        if hosp.get("id") == original_id:
                            # Check if city matches
                            if specialist_city.lower() in city.lower() or city.lower() in specialist_city.lower():
                                # Check if institution name matches
                                if specialist_institution and any(
                                    word.lower() in hosp.get("name", "").lower() 
                                    for word in specialist_institution.split() 
                                    if len(word) > 3
                                ):
                                    hospital_uuid = uuid_val
                                    break
                            if hospital_uuid:
                                break
                    if hospital_uuid:
                        break
                if hospital_uuid:
                    break
            
            doctor_row = {
                "id": str(uuid.uuid4()),  # Generate UUID
                "name": specialist.get("name", ""),
                "department": ", ".join(specialist.get("specialties", [])) if specialist.get("specialties") else specialist.get("title", "Oncology"),
                "consultation_fee": None,
                "rating": 4.8,  # Default for specialists
                "hospital_id": hospital_uuid,  # May be None if hospital not found
            }
            
            # Remove None values (except rating and hospital_id)
            doctor_row = {k: v for k, v in doctor_row.items() if v is not None or k in ("rating", "hospital_id")}
            doctors_list.append(doctor_row)
            specialist_counter += 1
    
    return doctors_list

def export_bed_inventory():
    """Export bed inventory data (placeholder - needs to be generated or provided)."""
    return []

def export_queue_snapshots():
    """Export queue snapshots (placeholder - needs to be generated or provided)."""
    return []

def main():
    print("Exporting seed data to JSON files...")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Export hospitals and get ID mapping
    print("Exporting hospitals...")
    hospitals, hospital_id_mapping = export_hospitals()
    hospitals_path = OUTPUT_DIR / "hospitals.json"
    with open(hospitals_path, "w", encoding="utf-8") as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported {len(hospitals)} hospitals to {hospitals_path}")
    
    # Save ID mapping for reference
    mapping_path = OUTPUT_DIR / "hospital_id_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(hospital_id_mapping, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved hospital ID mapping to {mapping_path}")
    
    # Export doctors (using hospital ID mapping)
    print("Exporting doctors...")
    doctors = export_doctors(hospital_id_mapping)
    doctors_path = OUTPUT_DIR / "doctors.json"
    with open(doctors_path, "w", encoding="utf-8") as f:
        json.dump(doctors, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported {len(doctors)} doctors to {doctors_path}")
    
    # Export bed inventory (empty for now)
    print("Exporting bed inventory...")
    bed_inventory = export_bed_inventory()
    bed_inventory_path = OUTPUT_DIR / "bed_inventory.json"
    with open(bed_inventory_path, "w", encoding="utf-8") as f:
        json.dump(bed_inventory, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported {len(bed_inventory)} bed inventory records to {bed_inventory_path}")
    
    # Export queue snapshots (empty for now)
    print("Exporting queue snapshots...")
    queue_snapshots = export_queue_snapshots()
    queue_snapshots_path = OUTPUT_DIR / "queue_snapshots.json"
    with open(queue_snapshots_path, "w", encoding="utf-8") as f:
        json.dump(queue_snapshots, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported {len(queue_snapshots)} queue snapshots to {queue_snapshots_path}")
    
    print("\n[OK] Export complete!")
    print(f"\nNext steps:")
    print(f"1. Review the JSON files in {OUTPUT_DIR}")
    print(f"2. Run: python supabase_seed.py")
    print(f"   (Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set)")

if __name__ == "__main__":
    main()




