from models import CostCalculationRequest, CostCalculationResponse, CostBreakdown
from typing import Dict, Any, List
import logging
from default_data import (
    DEFAULT_COUNTRY, DEFAULT_BASE_COSTS, DEFAULT_ACCOMMODATION_COSTS,
    HOSPITAL_TIER_MULTIPLIERS, DEFAULT_HOSPITAL_TIER_MULTIPLIER,
    ROOM_CATEGORY_MULTIPLIERS, REGIMEN_MULTIPLIERS, DRUG_ACCESS_MULTIPLIERS,
    RADIATION_TECHNIQUE_MULTIPLIERS, TRANSPLANT_TYPE_MULTIPLIERS,
    TRAVEL_TYPE_MULTIPLIERS, BASE_FLIGHT_COST_USD, LOCAL_TRANSPORT_COSTS,
    FOOD_COST_PER_DAY_USD, DEFAULT_INSURANCE_COVERAGE,
    normalize_number, clamp_number, get_country_data, get_base_costs, get_accommodation_costs
)

logger = logging.getLogger(__name__)

class CostCalculatorService:
    def __init__(self, db):
        self.db = db
    
    async def calculate_treatment_cost(self, request: CostCalculationRequest) -> CostCalculationResponse:
        """
        Main cost calculation engine with robust fallbacks.
        Formula: Total Cost = Clinical Cost + Non-clinical Cost - Insurance Coverage + Risk Buffer
        ALWAYS returns a result, never crashes.
        """
        assumptions: List[str] = []
        confidence_level = "High"
        
        try:
            # ========================================================================
            # 1. NORMALIZE & VALIDATE INPUTS
            # ========================================================================
            country_id = request.country or 'india'
            hospital_tier_id = request.hospital_tier or 'tier_3'
            
            # Normalize numeric inputs
            surgery_days = clamp_number(normalize_number(request.surgery_days, 3), 1, 30)
            icu_days = clamp_number(normalize_number(request.icu_days, 0), 0, 15)
            chemo_cycles = clamp_number(normalize_number(request.chemo_cycles, 6), 1, 24)
            radiation_fractions = clamp_number(normalize_number(request.radiation_fractions, 25), 1, 40)
            transplant_days = clamp_number(normalize_number(request.transplant_days, 30), 14, 60)
            pet_ct_count = clamp_number(normalize_number(request.pet_ct_count, 2), 0, 10)
            mri_ct_count = clamp_number(normalize_number(request.mri_ct_count, 4), 0, 20)
            opd_consults = clamp_number(normalize_number(request.opd_consults, 10), 1, 30)
            companions = clamp_number(normalize_number(request.companions, 1), 0, 5)
            stay_duration = clamp_number(normalize_number(request.stay_duration, 60), 7, 180)
            return_trips = clamp_number(normalize_number(request.return_trips, 1), 1, 5)
            complication_buffer = clamp_number(normalize_number(request.complication_buffer, 15), 0, 30)
            deductible = normalize_number(request.deductible, 0, 0)
            copay_percent = clamp_number(normalize_number(request.copay_percent, 20), 0, 50)
            
            # ========================================================================
            # 2. FETCH DATA WITH FALLBACKS
            # ========================================================================
            # Try to fetch from DB, fallback to defaults
            country = None
            try:
                if self.db:
                    country = await self.db.countries.find_one({'id': country_id})
            except Exception as e:
                logger.warning(f"Could not fetch country from DB: {e}")
            
            if not country:
                country = get_country_data(country_id)
                # Convert to dict format if needed (for backward compatibility)
                if not isinstance(country, dict):
                    country = {
                        'id': country.get('id', country_id),
                        'name': country.get('name', country_id),
                        'currency': country.get('currency_code', country.get('currency', 'USD')),
                        'currency_code': country.get('currency_code', country.get('currency', 'USD')),
                        'currency_symbol': country.get('currency_symbol', '$'),
                        'fx_rate': country.get('exchange_rate_to_usd', 1.0),
                        'exchange_rate_to_usd': country.get('exchange_rate_to_usd', 1.0),
                        'data_quality': country.get('data_quality', 'medium'),
                    }
                assumptions.append(f"Using default country data for {country_id}")
                confidence_level = "Medium" if confidence_level == "High" else confidence_level
            else:
                # Ensure country dict has all required fields
                if 'currency_code' not in country:
                    country['currency_code'] = country.get('currency', 'USD')
                if 'currency_symbol' not in country:
                    country['currency_symbol'] = '$'
                if 'exchange_rate_to_usd' not in country:
                    country['exchange_rate_to_usd'] = country.get('fx_rate', 1.0)
            
            # Fetch base costs with fallback
            base_costs = None
            try:
                if self.db:
                    base_costs = await self.db.base_costs.find_one({'country_id': country_id})
            except Exception as e:
                logger.warning(f"Could not fetch base costs from DB: {e}")
            
            if not base_costs:
                base_costs = get_base_costs(country_id)
                assumptions.append(f"Using default base costs for {country_id}")
                confidence_level = "Medium" if confidence_level == "High" else confidence_level
            
            # Fetch hospital tier with fallback
            tier_multiplier = DEFAULT_HOSPITAL_TIER_MULTIPLIER
            hospital_tier_name = "Tier 3 - Regional Private Hospital"
            try:
                if self.db:
                    hospital_tier = await self.db.hospital_tiers.find_one({'id': hospital_tier_id})
                    if hospital_tier:
                        tier_multiplier = normalize_number(hospital_tier.get('multiplier'), DEFAULT_HOSPITAL_TIER_MULTIPLIER)
                        hospital_tier_name = hospital_tier.get('name', hospital_tier_name)
            except Exception as e:
                logger.warning(f"Could not fetch hospital tier from DB: {e}")
            
            if tier_multiplier == DEFAULT_HOSPITAL_TIER_MULTIPLIER:
                tier_multiplier = HOSPITAL_TIER_MULTIPLIERS.get(hospital_tier_id, DEFAULT_HOSPITAL_TIER_MULTIPLIER)
            
            # Initialize breakdown
            breakdown = CostBreakdown()
            
            # ========================================================================
            # 3. CALCULATE CLINICAL COSTS
            # ========================================================================
            clinical_cost = 0.0
            
            # Surgery cost
            if request.include_surgery:
                surgery_cost = normalize_number(base_costs.get('surgery', 0)) * tier_multiplier
                room_cost = normalize_number(base_costs.get('room_per_day', 0)) * surgery_days
                icu_cost = normalize_number(base_costs.get('icu_per_day', 0)) * icu_days
                
                # Apply room category multiplier
                room_category = request.room_category or 'semi_private'
                room_mult = ROOM_CATEGORY_MULTIPLIERS.get(room_category, 1.0)
                room_cost *= room_mult
                
                total_surgery = surgery_cost + room_cost + icu_cost
                breakdown.surgery = round(total_surgery, 2)
                clinical_cost += total_surgery
                
                surgery_type = request.surgery_type or 'Not specified'
                assumptions.append(f"Surgery: {surgery_type}, {surgery_days} days ward + {icu_days} days ICU, Room: {room_category}")
            
            # Chemotherapy cost
            if request.include_chemo:
                base_chemo_cost = normalize_number(base_costs.get('chemo_per_cycle', 0))
                
                # Apply regimen type multiplier
                regimen_type = request.regimen_type or 'standard_chemo'
                regimen_mult = REGIMEN_MULTIPLIERS.get(regimen_type, 1.0)
                chemo_cost = base_chemo_cost * regimen_mult
                
                # Apply drug access multiplier
                drug_access = request.drug_access or 'generics'
                drug_mult = DRUG_ACCESS_MULTIPLIERS.get(drug_access, 0.6)
                chemo_cost *= drug_mult
                
                # Add day-care cost (assumed 10% of drug cost)
                daycare_cost = chemo_cost * 0.1
                
                total_chemo = (chemo_cost + daycare_cost) * chemo_cycles * tier_multiplier
                breakdown.chemotherapy = round(total_chemo, 2)
                clinical_cost += total_chemo
                
                assumptions.append(f"Chemotherapy: {chemo_cycles} cycles of {regimen_type}, Drug access: {drug_access}")
            
            # Radiation cost
            if request.include_radiation:
                base_radiation_cost = normalize_number(base_costs.get('radiation_per_fraction', 0))
                
                # Apply technique multiplier
                radiation_technique = request.radiation_technique or '3d_crt'
                technique_mult = RADIATION_TECHNIQUE_MULTIPLIERS.get(radiation_technique, 1.0)
                radiation_cost = base_radiation_cost * technique_mult
                total_radiation = radiation_cost * radiation_fractions * tier_multiplier
                
                # Add concurrent chemo cost if applicable
                if request.concurrent_chemo:
                    concurrent_chemo_cost = normalize_number(base_costs.get('chemo_per_cycle', 0)) * 0.3 * tier_multiplier
                    total_radiation += concurrent_chemo_cost
                    assumptions.append("Concurrent chemotherapy included with radiation")
                
                breakdown.radiation = round(total_radiation, 2)
                clinical_cost += total_radiation
                
                assumptions.append(f"Radiation: {radiation_fractions} fractions using {radiation_technique}")
            
            # Transplant cost
            if request.include_transplant:
                transplant_cost = normalize_number(base_costs.get('transplant', 0)) * tier_multiplier
                
                # Apply transplant type multiplier
                transplant_type = request.transplant_type or 'autologous'
                transplant_mult = TRANSPLANT_TYPE_MULTIPLIERS.get(transplant_type, 1.0)
                transplant_cost *= transplant_mult
                
                # Add hospitalization cost
                room_cost = normalize_number(base_costs.get('room_per_day', 0)) * transplant_days
                transplant_cost += room_cost
                
                breakdown.transplant = round(transplant_cost, 2)
                clinical_cost += transplant_cost
                
                assumptions.append(f"Transplant: {transplant_type}, {transplant_days} days hospitalization")
            
            # Diagnostics cost
            diagnostics_cost = 0.0
            diagnostics_cost += normalize_number(base_costs.get('pet_ct', 0)) * pet_ct_count
            diagnostics_cost += normalize_number(base_costs.get('mri_ct', 0)) * mri_ct_count
            if request.include_ngs:
                diagnostics_cost += normalize_number(base_costs.get('ngsp_panel', 0))
                assumptions.append("NGS panel testing included")
            diagnostics_cost += normalize_number(base_costs.get('opd_consult', 0)) * opd_consults
            
            breakdown.diagnostics = round(diagnostics_cost, 2)
            clinical_cost += diagnostics_cost
            
            if pet_ct_count > 0 or mri_ct_count > 0:
                assumptions.append(f"Diagnostics: {pet_ct_count} PET-CT, {mri_ct_count} MRI/CT scans, {opd_consults} OPD consultations")
            
            # ========================================================================
            # 4. CALCULATE NON-CLINICAL COSTS (Medical Tourism)
            # ========================================================================
            non_clinical_cost = 0.0
            
            # Accommodation
            accommodation_costs_data = None
            try:
                if self.db:
                    accommodation_costs_data = await self.db.accommodation_costs.find_one({'country_id': country_id})
            except Exception as e:
                logger.warning(f"Could not fetch accommodation costs from DB: {e}")
            
            if not accommodation_costs_data:
                accommodation_costs_data = get_accommodation_costs(country_id)
            
            accommodation_level = request.accommodation_level or 'mid'
            accommodation_rate = normalize_number(accommodation_costs_data.get(accommodation_level, 0), 0)
            total_accommodation = accommodation_rate * stay_duration * (companions + 1)
            breakdown.accommodation = round(total_accommodation, 2)
            non_clinical_cost += total_accommodation
            
            # Travel costs (estimated)
            travel_type = request.travel_type or 'economy'
            travel_mult = TRAVEL_TYPE_MULTIPLIERS.get(travel_type, 1.0)
            base_flight_cost = BASE_FLIGHT_COST_USD * normalize_number(country.get('fx_rate', 1.0))
            total_travel = base_flight_cost * travel_mult * return_trips * (companions + 1)
            breakdown.travel = round(total_travel, 2)
            non_clinical_cost += total_travel
            
            # Local transport
            local_transport = request.local_transport or 'daily_cab'
            daily_transport_usd = LOCAL_TRANSPORT_COSTS.get(local_transport, 30)
            daily_transport = daily_transport_usd * normalize_number(country.get('fx_rate', 1.0))
            total_transport = daily_transport * stay_duration
            breakdown.local_transport = round(total_transport, 2)
            non_clinical_cost += total_transport
            
            # Food allowance
            food_per_day = FOOD_COST_PER_DAY_USD * normalize_number(country.get('fx_rate', 1.0))
            total_food = food_per_day * stay_duration * (companions + 1)
            breakdown.food = round(total_food, 2)
            non_clinical_cost += total_food
            
            assumptions.append(f"Medical tourism: {companions} companion(s), {stay_duration} days, {accommodation_level} accommodation, {travel_type} travel")
            
            # ========================================================================
            # 5. APPLY COMPLICATION BUFFER
            # ========================================================================
            buffer_amount = clinical_cost * (complication_buffer / 100.0)
            
            # ========================================================================
            # 6. CALCULATE TOTAL BEFORE INSURANCE
            # ========================================================================
            total_before_insurance = clinical_cost + non_clinical_cost + buffer_amount
            
            # ========================================================================
            # 7. CALCULATE INSURANCE COVERAGE
            # ========================================================================
            insurance_pays = 0.0
            if request.has_insurance:
                insurer = None
                try:
                    if self.db and request.insurer:
                        insurer = await self.db.insurers.find_one({'id': request.insurer})
                except Exception as e:
                    logger.warning(f"Could not fetch insurer from DB: {e}")
                
                # Get coverage percentages
                if request.custom_coverage:
                    inpatient_cov = clamp_number(normalize_number(request.inpatient_coverage, 80), 0, 100) / 100.0
                    outpatient_cov = clamp_number(normalize_number(request.outpatient_coverage, 50), 0, 100) / 100.0
                    drug_cov = clamp_number(normalize_number(request.drug_coverage, 70), 0, 100) / 100.0
                    assumptions.append(f"Custom insurance coverage: Inpatient {inpatient_cov*100}%, Outpatient {outpatient_cov*100}%, Drugs {drug_cov*100}%")
                elif insurer:
                    inpatient_cov = normalize_number(insurer.get('inpatient_coverage', 80), 80) / 100.0
                    outpatient_cov = normalize_number(insurer.get('outpatient_coverage', 50), 50) / 100.0
                    drug_cov = normalize_number(insurer.get('drug_coverage', 70), 70) / 100.0
                    assumptions.append(f"Insurance: {insurer.get('name', 'Unknown')} - Inpatient {inpatient_cov*100}%, Outpatient {outpatient_cov*100}%, Drugs {drug_cov*100}%")
                else:
                    # Use defaults
                    default_cov = DEFAULT_INSURANCE_COVERAGE
                    inpatient_cov = default_cov['inpatient_coverage'] / 100.0
                    outpatient_cov = default_cov['outpatient_coverage'] / 100.0
                    drug_cov = default_cov['drug_coverage'] / 100.0
                    assumptions.append(f"Using default insurance coverage: Inpatient {inpatient_cov*100}%, Outpatient {outpatient_cov*100}%, Drugs {drug_cov*100}%")
                    confidence_level = "Medium" if confidence_level == "High" else confidence_level
                
                # Calculate covered amounts
                # Inpatient: Surgery, Transplant, Hospitalization
                inpatient_eligible = breakdown.surgery + breakdown.transplant
                inpatient_covered = inpatient_eligible * inpatient_cov
                
                # Outpatient: Radiation, Diagnostics
                outpatient_eligible = breakdown.radiation + breakdown.diagnostics
                outpatient_covered = outpatient_eligible * outpatient_cov
                
                # Drugs: Chemotherapy
                drug_covered = breakdown.chemotherapy * drug_cov
                
                total_covered = inpatient_covered + outpatient_covered + drug_covered
                
                # Apply deductible
                covered_after_deductible = max(0.0, total_covered - deductible)
                
                # Apply co-pay
                insurance_pays = covered_after_deductible * (1.0 - copay_percent / 100.0)
                
                assumptions.append(f"Insurance deductible: {deductible} {country.get('currency', 'USD')}, Co-pay: {copay_percent}%")
            else:
                assumptions.append("No insurance coverage")
            
            # ========================================================================
            # 8. CALCULATE FINAL OUT-OF-POCKET
            # ========================================================================
            patient_out_of_pocket = max(0.0, total_before_insurance - insurance_pays)
            
            # ========================================================================
            # 9. CURRENCY CONVERSIONS
            # ========================================================================
            # Get exchange rate to USD (from country data)
            exchange_rate_to_usd = normalize_number(
                country.get('exchange_rate_to_usd', 1.0), 
                1.0
            )
            currency_code = country.get('currency_code', country.get('currency', 'USD'))
            currency_symbol = country.get('currency_symbol', '$')
            
            # Convert local currency to USD
            # If local currency is USD, no conversion needed
            if currency_code == 'USD':
                total_cost_usd = total_before_insurance
                clinical_cost_usd = clinical_cost
                non_clinical_cost_usd = non_clinical_cost
                insurance_pays_usd = insurance_pays
                patient_out_of_pocket_usd = patient_out_of_pocket
            else:
                # Convert from local currency to USD
                # exchange_rate_to_usd = local_currency_per_usd
                # So: usd = local / exchange_rate_to_usd
                total_cost_usd = total_before_insurance / exchange_rate_to_usd
                clinical_cost_usd = clinical_cost / exchange_rate_to_usd
                non_clinical_cost_usd = non_clinical_cost / exchange_rate_to_usd
                insurance_pays_usd = insurance_pays / exchange_rate_to_usd
                patient_out_of_pocket_usd = patient_out_of_pocket / exchange_rate_to_usd
            
            # Convert to INR (for backward compatibility)
            # Use exchange_rate_to_usd to get USD first, then convert USD to INR
            usd_to_inr_rate = 89.899376  # 1 USD = 89.899376 INR (Dec 29, 2025 21:01 UTC)
            total_in_inr = total_cost_usd * usd_to_inr_rate
            
            # Create USD breakdown
            breakdown_usd = CostBreakdown(
                surgery=round(breakdown.surgery / exchange_rate_to_usd if currency_code != 'USD' else breakdown.surgery, 2),
                chemotherapy=round(breakdown.chemotherapy / exchange_rate_to_usd if currency_code != 'USD' else breakdown.chemotherapy, 2),
                radiation=round(breakdown.radiation / exchange_rate_to_usd if currency_code != 'USD' else breakdown.radiation, 2),
                transplant=round(breakdown.transplant / exchange_rate_to_usd if currency_code != 'USD' else breakdown.transplant, 2),
                diagnostics=round(breakdown.diagnostics / exchange_rate_to_usd if currency_code != 'USD' else breakdown.diagnostics, 2),
                accommodation=round(breakdown.accommodation / exchange_rate_to_usd if currency_code != 'USD' else breakdown.accommodation, 2),
                travel=round(breakdown.travel / exchange_rate_to_usd if currency_code != 'USD' else breakdown.travel, 2),
                local_transport=round(breakdown.local_transport / exchange_rate_to_usd if currency_code != 'USD' else breakdown.local_transport, 2),
                food=round(breakdown.food / exchange_rate_to_usd if currency_code != 'USD' else breakdown.food, 2),
            )
            
            # ========================================================================
            # 10. FINALIZE ASSUMPTIONS
            # ========================================================================
            if currency_code == 'USD':
                assumptions.insert(0, f"Currency: {currency_code} (base currency)")
            else:
                assumptions.insert(0, f"Exchange rate: 1 USD = {exchange_rate_to_usd} {currency_code} (reference rate as of Dec 29, 2025 21:01 UTC)")
                assumptions.insert(1, f"Converted to USD using exchange rate: {exchange_rate_to_usd}")
            
            assumptions.insert(len(assumptions) - 3, f"Hospital tier: {hospital_tier_name} (multiplier: {tier_multiplier}x)")
            assumptions.append(f"Complication buffer: {complication_buffer}%")
            assumptions.append(f"Confidence level: {confidence_level}")
            assumptions.append(f"Country-level baseline data used for {country.get('name', 'selected country')}")
            assumptions.append(f"Estimate based on data updated: Dec 29, 2025 (v3.1 - Multi-country with updated exchange rates)")
            
            # Add data quality note
            data_quality = country.get('data_quality', 'medium')
            if data_quality == 'medium':
                assumptions.append("⚠️ Using conservative national averages - city-level pricing not available")
                if confidence_level == "High":
                    confidence_level = "Medium"
            
            # Add missing input assumptions
            if not request.include_surgery and not request.include_chemo and not request.include_radiation and not request.include_transplant:
                assumptions.append("⚠️ No treatment modalities selected - estimate includes diagnostics only")
                confidence_level = "Low"
            
            if not request.cancer_type:
                assumptions.append("⚠️ Cancer type not specified - using generic cost estimates")
                confidence_level = "Low"
            
            if not request.stage:
                assumptions.append("⚠️ Stage not specified - using average stage cost estimates")
                confidence_level = "Low"
            
            # ========================================================================
            # 11. BUILD RESPONSE
            # ========================================================================
            response = CostCalculationResponse(
                total_cost_local=round(total_before_insurance, 2),
                total_cost_usd=round(total_cost_usd, 2),
                total_cost_inr=round(total_in_inr, 2),
                clinical_cost=round(clinical_cost, 2),
                clinical_cost_usd=round(clinical_cost_usd, 2),
                non_clinical_cost=round(non_clinical_cost, 2),
                non_clinical_cost_usd=round(non_clinical_cost_usd, 2),
                insurance_pays=round(insurance_pays, 2),
                insurance_pays_usd=round(insurance_pays_usd, 2),
                patient_out_of_pocket=round(patient_out_of_pocket, 2),
                patient_out_of_pocket_usd=round(patient_out_of_pocket_usd, 2),
                breakdown=breakdown,
                breakdown_usd=breakdown_usd,
                currency_code=currency_code,
                currency_symbol=currency_symbol,
                exchange_rate_to_usd=exchange_rate_to_usd,
                assumptions=assumptions
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}", exc_info=True)
            # Return a safe fallback response instead of raising
            try:
                # Try to get at least country data
                country = get_country_data(request.country if request else 'india')
                fx_rate = normalize_number(country.get('fx_rate', 83.0), 83.0)
                
                # Return minimal safe estimate
                breakdown = CostBreakdown()
                breakdown.diagnostics = 1000 * fx_rate  # Minimal diagnostic cost
                
                exchange_rate_to_usd = normalize_number(country.get('exchange_rate_to_usd', 1.0), 1.0)
                currency_code = country.get('currency_code', country.get('currency', 'USD'))
                currency_symbol = country.get('currency_symbol', '$')
                local_cost = 1000 * normalize_number(country.get('fx_rate', 83.0), 83.0)
                usd_cost = local_cost / exchange_rate_to_usd if currency_code != 'USD' else local_cost
                
                return CostCalculationResponse(
                    total_cost_local=round(local_cost, 2),
                    total_cost_usd=round(usd_cost, 2),
                    total_cost_inr=round(usd_cost * 83.0, 2),
                    clinical_cost=round(local_cost, 2),
                    clinical_cost_usd=round(usd_cost, 2),
                    non_clinical_cost=0.0,
                    non_clinical_cost_usd=0.0,
                    insurance_pays=0.0,
                    insurance_pays_usd=0.0,
                    patient_out_of_pocket=round(local_cost, 2),
                    patient_out_of_pocket_usd=round(usd_cost, 2),
                    breakdown=breakdown,
                    breakdown_usd=CostBreakdown(),
                    currency_code=currency_code,
                    currency_symbol=currency_symbol,
                    exchange_rate_to_usd=exchange_rate_to_usd,
                    assumptions=[
                        "⚠️ Calculation error occurred - showing conservative estimate",
                        f"Please verify your inputs and try again",
                        f"Error: {str(e)}"
                    ]
                )
            except Exception as fallback_error:
                logger.error(f"Even fallback failed: {str(fallback_error)}")
                # Absolute last resort
                breakdown = CostBreakdown()
                usd_to_inr_rate = 89.899376  # Dec 29, 2025
                return CostCalculationResponse(
                    total_cost_local=50000.0,
                    total_cost_usd=50000.0,
                    total_cost_inr=round(50000.0 * usd_to_inr_rate, 2),
                    clinical_cost=50000.0,
                    clinical_cost_usd=50000.0,
                    non_clinical_cost=0.0,
                    non_clinical_cost_usd=0.0,
                    insurance_pays=0.0,
                    insurance_pays_usd=0.0,
                    patient_out_of_pocket=50000.0,
                    patient_out_of_pocket_usd=50000.0,
                    breakdown=breakdown,
                    breakdown_usd=breakdown,
                    currency_code='USD',
                    currency_symbol='$',
                    exchange_rate_to_usd=1.0,
                    assumptions=[
                        "⚠️ Critical error - unable to calculate estimate",
                        "Please contact support or try again later"
                    ]
                )
