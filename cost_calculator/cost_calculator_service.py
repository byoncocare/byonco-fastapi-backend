from models import CostCalculationRequest, CostCalculationResponse, CostBreakdown
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CostCalculatorService:
    def __init__(self, db):
        self.db = db
    
    async def calculate_treatment_cost(self, request: CostCalculationRequest) -> CostCalculationResponse:
        """
        Main cost calculation engine.
        Formula: Total Cost = Clinical Cost + Non-clinical Cost - Insurance Coverage + Risk Buffer
        """
        try:
            # Fetch base data
            country = await self.db.countries.find_one({'id': request.country})
            if not country:
                raise ValueError(f"Country {request.country} not found")
            
            base_costs = await self.db.base_costs.find_one({'country_id': request.country})
            if not base_costs:
                raise ValueError(f"Base costs for {request.country} not found")
            
            hospital_tier = await self.db.hospital_tiers.find_one({'id': request.hospital_tier})
            tier_multiplier = hospital_tier['multiplier'] if hospital_tier else 1.0
            
            # Initialize breakdown
            breakdown = CostBreakdown()
            
            # 1. Calculate Clinical Costs
            clinical_cost = 0
            
            # Surgery cost
            if request.include_surgery:
                surgery_cost = base_costs['surgery'] * tier_multiplier
                room_cost = base_costs['room_per_day'] * request.surgery_days
                icu_cost = base_costs['icu_per_day'] * request.icu_days
                
                # Apply room category multiplier
                room_multipliers = {
                    'general': 0.8,
                    'semi_private': 1.0,
                    'private': 1.5,
                    'deluxe': 2.0
                }
                room_cost *= room_multipliers.get(request.room_category, 1.0)
                
                total_surgery = surgery_cost + room_cost + icu_cost
                breakdown.surgery = round(total_surgery, 2)
                clinical_cost += total_surgery
            
            # Chemotherapy cost
            if request.include_chemo:
                base_chemo_cost = base_costs['chemo_per_cycle']
                
                # Apply regimen type multiplier
                regimen_multipliers = {
                    'standard_chemo': 1.0,
                    'targeted': 2.5,
                    'immunotherapy': 3.5,
                    'oral_tki': 2.0,
                    'combination': 4.0
                }
                chemo_cost = base_chemo_cost * regimen_multipliers.get(request.regimen_type, 1.0)
                
                # Apply drug access multiplier
                drug_multipliers = {
                    'originator': 1.0,
                    'generics': 0.6,
                    'biosimilars': 0.7
                }
                chemo_cost *= drug_multipliers.get(request.drug_access, 1.0)
                
                # Add day-care cost (assumed 10% of drug cost)
                daycare_cost = chemo_cost * 0.1
                
                total_chemo = (chemo_cost + daycare_cost) * request.chemo_cycles * tier_multiplier
                breakdown.chemotherapy = round(total_chemo, 2)
                clinical_cost += total_chemo
            
            # Radiation cost
            if request.include_radiation:
                base_radiation_cost = base_costs['radiation_per_fraction']
                
                # Apply technique multiplier
                technique_multipliers = {
                    '2d': 0.5,
                    '3d_crt': 1.0,
                    'imrt': 1.5,
                    'vmat': 1.8,
                    'sbrt': 2.5,
                    'proton': 5.0
                }
                radiation_cost = base_radiation_cost * technique_multipliers.get(request.radiation_technique, 1.0)
                total_radiation = radiation_cost * request.radiation_fractions * tier_multiplier
                
                # Add concurrent chemo cost if applicable
                if request.concurrent_chemo:
                    concurrent_chemo_cost = base_costs['chemo_per_cycle'] * 0.3 * tier_multiplier
                    total_radiation += concurrent_chemo_cost
                
                breakdown.radiation = round(total_radiation, 2)
                clinical_cost += total_radiation
            
            # Transplant cost
            if request.include_transplant:
                transplant_cost = base_costs['transplant'] * tier_multiplier
                
                # Apply transplant type multiplier
                transplant_multipliers = {
                    'autologous': 1.0,
                    'allogeneic': 1.8
                }
                transplant_cost *= transplant_multipliers.get(request.transplant_type, 1.0)
                
                # Add hospitalization cost
                room_cost = base_costs['room_per_day'] * request.transplant_days
                transplant_cost += room_cost
                
                breakdown.transplant = round(transplant_cost, 2)
                clinical_cost += transplant_cost
            
            # Diagnostics cost
            diagnostics_cost = 0
            diagnostics_cost += base_costs['pet_ct'] * request.pet_ct_count
            diagnostics_cost += base_costs['mri_ct'] * request.mri_ct_count
            if request.include_ngs:
                diagnostics_cost += base_costs['ngsp_panel']
            diagnostics_cost += base_costs['opd_consult'] * request.opd_consults
            
            breakdown.diagnostics = round(diagnostics_cost, 2)
            clinical_cost += diagnostics_cost
            
            # 2. Calculate Non-clinical Costs (Medical Tourism)
            non_clinical_cost = 0
            
            # Accommodation
            accommodation_costs = await self.db.accommodation_costs.find_one({'country_id': request.country})
            if accommodation_costs:
                accommodation_rate = accommodation_costs.get(request.accommodation_level, 0)
                total_accommodation = accommodation_rate * request.stay_duration * (request.companions + 1)
                breakdown.accommodation = round(total_accommodation, 2)
                non_clinical_cost += total_accommodation
            
            # Travel costs (estimated)
            travel_multipliers = {'economy': 1.0, 'premium': 1.8, 'business': 3.5}
            base_flight_cost = 500 * country['fx_rate']  # Base flight in local currency
            total_travel = base_flight_cost * travel_multipliers.get(request.travel_type, 1.0) * request.return_trips * (request.companions + 1)
            breakdown.travel = round(total_travel, 2)
            non_clinical_cost += total_travel
            
            # Local transport
            transport_costs = {'daily_cab': 30, 'public': 10, 'hospital_shuttle': 5}
            daily_transport = transport_costs.get(request.local_transport, 30) * country['fx_rate']
            total_transport = daily_transport * request.stay_duration
            breakdown.local_transport = round(total_transport, 2)
            non_clinical_cost += total_transport
            
            # Food allowance
            food_per_day = 50 * country['fx_rate']  # Base food cost
            total_food = food_per_day * request.stay_duration * (request.companions + 1)
            breakdown.food = round(total_food, 2)
            non_clinical_cost += total_food
            
            # 3. Apply Complication Buffer
            buffer_amount = clinical_cost * (request.complication_buffer / 100)
            
            # 4. Calculate Total Before Insurance
            total_before_insurance = clinical_cost + non_clinical_cost + buffer_amount
            
            # 5. Calculate Insurance Coverage
            insurance_pays = 0
            if request.has_insurance and request.insurer:
                insurer = await self.db.insurers.find_one({'id': request.insurer})
                
                if insurer:
                    # Get coverage percentages
                    if request.custom_coverage:
                        inpatient_cov = request.inpatient_coverage / 100
                        outpatient_cov = request.outpatient_coverage / 100
                        drug_cov = request.drug_coverage / 100
                    else:
                        inpatient_cov = insurer['inpatient_coverage'] / 100
                        outpatient_cov = insurer['outpatient_coverage'] / 100
                        drug_cov = insurer['drug_coverage'] / 100
                    
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
                    covered_after_deductible = max(0, total_covered - request.deductible)
                    
                    # Apply co-pay
                    insurance_pays = covered_after_deductible * (1 - request.copay_percent / 100)
            
            # 6. Calculate Final Out-of-Pocket
            patient_out_of_pocket = total_before_insurance - insurance_pays
            
            # 7. Convert to INR
            total_in_inr = total_before_insurance * country['fx_rate']
            
            # 8. Generate Assumptions
            assumptions = [
                f"Exchange rate: 1 {country['currency']} = {country['fx_rate']} INR",
                f"Hospital tier: {hospital_tier['name']} (multiplier: {tier_multiplier}x)",
                f"Complication buffer: {request.complication_buffer}%",
                f"Estimate based on data updated: Nov 2025 (v1.0)"
            ]
            
            if request.include_surgery:
                assumptions.append(f"Surgery: {request.surgery_days} days ward + {request.icu_days} days ICU, Room: {request.room_category}")
            
            if request.include_chemo:
                assumptions.append(f"Chemotherapy: {request.chemo_cycles} cycles of {request.regimen_type}, Drug access: {request.drug_access}")
            
            if request.include_radiation:
                assumptions.append(f"Radiation: {request.radiation_fractions} fractions using {request.radiation_technique}")
            
            if request.has_insurance:
                assumptions.append(f"Insurance coverage applied with deductible: {request.deductible} {country['currency']} and co-pay: {request.copay_percent}%")
            
            # Build response
            response = CostCalculationResponse(
                total_cost_local=round(total_before_insurance, 2),
                total_cost_inr=round(total_in_inr, 2),
                clinical_cost=round(clinical_cost, 2),
                non_clinical_cost=round(non_clinical_cost, 2),
                insurance_pays=round(insurance_pays, 2),
                patient_out_of_pocket=round(patient_out_of_pocket, 2),
                breakdown=breakdown,
                currency=country['currency'],
                assumptions=assumptions
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            raise
