"""
Export seed data from data_seed.py to JSON files for Supabase seeding.
This script converts the Python data structures into JSON format matching Supabase schema.
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
import uuid
from datetime import datetime

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

def export_hospitals():
    """Export hospitals data, flattening the city-keyed dict into a list."""
    hospitals_list = []
    
    for city, city_hospitals in HOSPITALS.items():
        for hospital in city_hospitals:
            # Map to Supabase schema
            # Note: Supabase uses UUID for id, so we'll let it generate UUIDs
            # Store the original ID in external_ref for reference
            original_id = hospital.get("id", "")
            
            hospital_row = {
                # Don't include id - let Supabase generate UUID
                # Store original ID in external_ref for reference
                "external_ref": original_id,
                "name": hospital.get("name", ""),
                "city": hospital.get("city", city),
                "address": hospital.get("address", ""),
                "min_estimated_cost": hospital.get("cost_range", {}).get("min"),
                "rating": float(hospital.get("rating", 0)) if hospital.get("rating") else None,
                "phone": hospital.get("phone"),
                "is_active": True,
            }
            
            # Add lat/lng if available (they're not in the seed data structure, so leave None)
            # You can add these later via geocoding or manual entry
            
            # Extract phone if it's in a contact field
            if not hospital_row["phone"] and "contact" in hospital:
                hospital_row["phone"] = hospital["contact"]
            
            # Add tier if available (will need migration to add this column)
            # Store as comment for now - uncomment after adding tier column
            # if "tier" in hospital:
            #     tier_str = hospital["tier"]
            #     if "Tier 1" in tier_str:
            #         hospital_row["tier"] = "Tier 1"
            #     elif "Tier 2" in tier_str:
            #         hospital_row["tier"] = "Tier 2"
            #     elif "Tier 3" in tier_str:
            #         hospital_row["tier"] = "Tier 3"
            #     else:
            #         hospital_row["tier"] = "Tier 2"  # Default
            
            # Remove None values to avoid issues (except for optional fields)
            # Keep rating even if None for now
            hospital_row = {k: v for k, v in hospital_row.items() if v is not None or k == "rating"}
            
            hospitals_list.append(hospital_row)
    
    return hospitals_list

def export_doctors():
    """Export doctors data, including specialists."""
    doctors_list = []
    
    # Regular doctors from DOCTORS list
    for doctor in DOCTORS:
        # Map hospital_id from string to UUID (will need to look up in hospitals table)
        # For now, we'll need to handle this after hospitals are seeded
        # Store original hospital_id string for reference
        original_hospital_id = doctor.get("hospital_id")
        
        doctor_row = {
            # Don't include id - let Supabase generate UUID
            "name": doctor.get("name", ""),
            "department": doctor.get("specialty", "Oncology"),
            "consultation_fee": None,  # Not in seed data
            "rating": float(doctor.get("rating", 0)) if doctor.get("rating") else None,
            # Note: hospital_id needs to be UUID from hospitals table
            # We'll need to update this after hospitals are seeded, or use a lookup
            # For now, leave as None and update manually or via script
            "hospital_id": None,  # Will need to be updated after hospitals are seeded
        }
        
        # Store original hospital_id in a comment/note field if available
        # Or we can create a mapping file
        
        # Remove None values (except rating which can be None)
        doctor_row = {k: v for k, v in doctor_row.items() if v is not None or k == "rating"}
        doctors_list.append(doctor_row)
    
    # Add specialists from RARE_CANCER_SPECIALISTS and COMMON_CANCER_SPECIALISTS
    all_specialists = {**RARE_CANCER_SPECIALISTS, **COMMON_CANCER_SPECIALISTS}
    
    specialist_counter = len(doctors_list) + 1
    for cancer_name, specialists in all_specialists.items():
        for specialist in specialists:
            # Try to find hospital_id by matching city/institution
            hospital_id = None
            specialist_city = specialist.get("city", "")
            specialist_institution = specialist.get("institution", "")
            
            # Try to match with hospitals
            for city, city_hospitals in HOSPITALS.items():
                if specialist_city.lower() in city.lower() or city.lower() in specialist_city.lower():
                    for hosp in city_hospitals:
                        if specialist_institution and any(
                            word.lower() in hosp.get("name", "").lower() 
                            for word in specialist_institution.split() 
                            if len(word) > 3
                        ):
                            hospital_id = hosp.get("id")
                            break
                    if hospital_id:
                        break
                if hospital_id:
                    break
            
            doctor_row = {
                # Don't include id - let Supabase generate UUID
                "name": specialist.get("name", ""),
                "department": ", ".join(specialist.get("specialties", [])) if specialist.get("specialties") else specialist.get("title", "Oncology"),
                "consultation_fee": None,
                "rating": 4.8,  # Default for specialists
                # hospital_id will be None if not matched, can be updated later
                "hospital_id": hospital_id,  # May be None if hospital not found
            }
            
            # Remove None values (except rating)
            doctor_row = {k: v for k, v in doctor_row.items() if v is not None or k == "rating"}
            doctors_list.append(doctor_row)
            specialist_counter += 1
    
    return doctors_list

def export_bed_inventory():
    """Export bed inventory data (placeholder - needs to be generated or provided)."""
    # This would need actual bed inventory data
    # For now, return empty list - can be populated later
    return []

def export_queue_snapshots():
    """Export queue snapshots (placeholder - needs to be generated or provided)."""
    # This would need actual queue snapshot data
    # For now, return empty list - can be populated later
    return []

def main():
    print("Exporting seed data to JSON files...")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Export hospitals
    print("Exporting hospitals...")
    hospitals = export_hospitals()
    hospitals_path = OUTPUT_DIR / "hospitals.json"
    with open(hospitals_path, "w", encoding="utf-8") as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Exported {len(hospitals)} hospitals to {hospitals_path}")
    
    # Export doctors
    print("Exporting doctors...")
    doctors = export_doctors()
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

