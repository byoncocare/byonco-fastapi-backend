# Cost Calculator Failure Points Analysis

## A) Current Failure Points

### 1. Backend Service (`cost_calculator_service.py`)
- **Line 18-20**: If country not found in MongoDB → raises ValueError (no fallback to default data)
- **Line 22-24**: If base_costs not found → raises ValueError (no fallback)
- **Line 26-27**: If hospital_tier not found → uses 1.0, but `hospital_tier` could be None causing KeyError on line 218
- **Line 140**: If accommodation_costs not found → returns None, then line 142 tries `.get()` on None → AttributeError
- **Line 176**: If insurer not found → returns None, then line 185 tries `insurer['inpatient_coverage']` → TypeError
- **No input validation**: Numeric fields could be NaN, null, negative, or out of range
- **Missing optional fields**: surgery_type, regimen_type, radiation_technique, transplant_type are Optional but used without null checks

### 2. Frontend (`CostCalculatorPage.jsx`)
- **Line 252-272**: If backend response missing fields → mapping fails with undefined errors
- **Line 1190**: If `costResult.totalCostLocal` is undefined/NaN → displays "NaN" or crashes
- **Line 1237**: If `costResult.breakdown` missing fields → Object.entries fails
- **No fallback**: If API call fails completely, user sees blank screen

### 3. Data Layer
- **Backend expects MongoDB**: No guarantee data is seeded, no fallback to defaults
- **Frontend has hardcoded data**: `costCalculatorData.js` exists but backend doesn't use it
- **No single source of truth**: Data split between frontend JS and backend MongoDB

## B) Payload Schema (All Input Keys)

From `CostCalculationRequest` model:
- country, city, hospital_tier, accreditation
- age_group, cancer_category, cancer_type, stage, intent
- include_surgery, surgery_type, surgery_days, icu_days, room_category
- include_chemo, regimen_type, chemo_cycles, drug_access
- include_radiation, radiation_technique, radiation_fractions, concurrent_chemo
- include_transplant, transplant_type, transplant_days
- pet_ct_count, mri_ct_count, include_ngs, opd_consults, follow_up_months
- has_insurance, insurer, policy_type, custom_coverage, inpatient_coverage, outpatient_coverage, drug_coverage, deductible, copay_percent
- companions, stay_duration, accommodation_level, travel_type, return_trips, local_transport
- complication_buffer, currency


