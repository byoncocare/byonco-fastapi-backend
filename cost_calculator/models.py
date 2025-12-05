from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

# Country Model
class Country(BaseModel):
    id: str
    name: str
    currency: str
    fx_rate: float

# Insurer Model
class Insurer(BaseModel):
    id: str
    country_id: str
    name: str
    is_global: bool = False
    inpatient_coverage: int
    outpatient_coverage: int
    drug_coverage: int

# Cancer Type Model
class CancerType(BaseModel):
    id: str
    name: str
    category: str  # common, rare, ultra-rare

# Stage Model
class Stage(BaseModel):
    id: str
    name: str
    description: str

# Hospital Tier Model
class HospitalTier(BaseModel):
    id: str
    name: str
    multiplier: float

# Base Costs Model
class BaseCosts(BaseModel):
    country_id: str
    surgery: float
    chemo_per_cycle: float
    radiation_per_fraction: float
    transplant: float
    pet_ct: float
    mri_ct: float
    ngsp_panel: float
    opd_consult: float
    room_per_day: float
    icu_per_day: float

# Accommodation Costs Model
class AccommodationCosts(BaseModel):
    country_id: str
    budget: float
    mid: float
    premium: float

# Cost Calculation Request Model
class CostCalculationRequest(BaseModel):
    # Country & Hospital
    country: str
    city: Optional[str] = None
    hospital_tier: str
    accreditation: List[str] = []
    
    # Patient & Disease
    age_group: str
    cancer_category: str
    cancer_type: str
    stage: str
    intent: str
    
    # Treatment - Surgery
    include_surgery: bool = False
    surgery_type: Optional[str] = None
    surgery_days: int = 3
    icu_days: int = 0
    room_category: str = 'semi_private'
    
    # Treatment - Chemotherapy
    include_chemo: bool = False
    regimen_type: Optional[str] = None
    chemo_cycles: int = 6
    drug_access: str = 'generics'
    
    # Treatment - Radiation
    include_radiation: bool = False
    radiation_technique: Optional[str] = None
    radiation_fractions: int = 25
    concurrent_chemo: bool = False
    
    # Treatment - Transplant
    include_transplant: bool = False
    transplant_type: Optional[str] = None
    transplant_days: int = 30
    
    # Diagnostics
    pet_ct_count: int = 2
    mri_ct_count: int = 4
    include_ngs: bool = False
    opd_consults: int = 10
    follow_up_months: int = 12
    
    # Insurance
    has_insurance: bool = False
    insurer: Optional[str] = None
    policy_type: str = 'domestic'
    custom_coverage: bool = False
    inpatient_coverage: int = 80
    outpatient_coverage: int = 50
    drug_coverage: int = 70
    deductible: float = 0
    copay_percent: int = 20
    
    # Medical Tourism
    companions: int = 1
    stay_duration: int = 60
    accommodation_level: str = 'mid'
    travel_type: str = 'economy'
    return_trips: int = 1
    local_transport: str = 'daily_cab'
    
    # Admin
    complication_buffer: int = 15
    currency: str = 'USD'

# Cost Breakdown Model
class CostBreakdown(BaseModel):
    surgery: float = 0
    chemotherapy: float = 0
    radiation: float = 0
    transplant: float = 0
    diagnostics: float = 0
    accommodation: float = 0
    travel: float = 0
    local_transport: float = 0
    food: float = 0

# Cost Calculation Response Model
class CostCalculationResponse(BaseModel):
    total_cost_local: float
    total_cost_inr: float
    clinical_cost: float
    non_clinical_cost: float
    insurance_pays: float
    patient_out_of_pocket: float
    breakdown: CostBreakdown
    currency: str
    assumptions: List[str] = []
