from fastapi import APIRouter, HTTPException, Query
from models import (
    Country, Insurer, CancerType, Stage, HospitalTier,
    CostCalculationRequest, CostCalculationResponse
)
from cost_calculator_service import CostCalculatorService
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

def create_api_router(db):
    router = APIRouter(prefix="/api/cost-calculator")
    calculator_service = CostCalculatorService(db)
    
    @router.get("/countries", response_model=List[Country])
    async def get_countries():
        """Get all available countries"""
        try:
            countries = await db.countries.find().to_list(100)
            return countries
        except Exception as e:
            logger.error(f"Error fetching countries: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch countries")
    
    @router.get("/insurers/{country_id}", response_model=List[Insurer])
    async def get_insurers_by_country(country_id: str):
        """Get all insurers for a specific country"""
        try:
            insurers = await db.insurers.find({'country_id': country_id}).to_list(100)
            return insurers
        except Exception as e:
            logger.error(f"Error fetching insurers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch insurers")
    
    @router.get("/cancer-types", response_model=List[CancerType])
    async def get_cancer_types():
        """Get all cancer types"""
        try:
            cancer_types = await db.cancer_types.find().to_list(100)
            return cancer_types
        except Exception as e:
            logger.error(f"Error fetching cancer types: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch cancer types")
    
    @router.get("/stages", response_model=List[Stage])
    async def get_stages():
        """Get all cancer stages"""
        try:
            stages = await db.stages.find().to_list(100)
            return stages
        except Exception as e:
            logger.error(f"Error fetching stages: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch stages")
    
    @router.get("/hospital-tiers", response_model=List[HospitalTier])
    async def get_hospital_tiers():
        """Get all hospital tiers"""
        try:
            tiers = await db.hospital_tiers.find().to_list(100)
            return tiers
        except Exception as e:
            logger.error(f"Error fetching hospital tiers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch hospital tiers")
    
    @router.post("/calculate-cost", response_model=CostCalculationResponse)
    async def calculate_cost(request: CostCalculationRequest):
        """Calculate treatment cost based on all input parameters"""
        try:
            result = await calculator_service.calculate_treatment_cost(request)
            return result
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to calculate cost")
    
    @router.post("/seed-database")
    async def seed_database(secret: str = Query(..., description="Secret key to authorize seeding")):
        """Seed the database with initial data. Requires secret key for security."""
        # Simple security: check if secret matches (set this in your environment variables)
        expected_secret = os.environ.get("SEED_SECRET_KEY", "change-me-in-production")
        if secret != expected_secret:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        try:
            from seed_data import (
                COUNTRIES_DATA, INSURERS_DATA, CANCER_TYPES_DATA,
                STAGES_DATA, HOSPITAL_TIERS_DATA, BASE_COSTS_DATA,
                ACCOMMODATION_COSTS_DATA
            )
            
            # Clear existing data
            await db.countries.delete_many({})
            await db.insurers.delete_many({})
            await db.cancer_types.delete_many({})
            await db.stages.delete_many({})
            await db.hospital_tiers.delete_many({})
            await db.base_costs.delete_many({})
            await db.accommodation_costs.delete_many({})
            
            # Insert countries
            await db.countries.insert_many(COUNTRIES_DATA)
            countries_count = len(COUNTRIES_DATA)
            
            # Insert insurers
            all_insurers = []
            for country_insurers in INSURERS_DATA.values():
                all_insurers.extend(country_insurers)
            await db.insurers.insert_many(all_insurers)
            insurers_count = len(all_insurers)
            
            # Insert cancer types
            await db.cancer_types.insert_many(CANCER_TYPES_DATA)
            cancer_types_count = len(CANCER_TYPES_DATA)
            
            # Insert stages
            await db.stages.insert_many(STAGES_DATA)
            stages_count = len(STAGES_DATA)
            
            # Insert hospital tiers
            await db.hospital_tiers.insert_many(HOSPITAL_TIERS_DATA)
            tiers_count = len(HOSPITAL_TIERS_DATA)
            
            # Insert base costs
            await db.base_costs.insert_many(BASE_COSTS_DATA)
            base_costs_count = len(BASE_COSTS_DATA)
            
            # Insert accommodation costs
            await db.accommodation_costs.insert_many(ACCOMMODATION_COSTS_DATA)
            accommodation_count = len(ACCOMMODATION_COSTS_DATA)
            
            return {
                "message": "Database seeded successfully",
                "counts": {
                    "countries": countries_count,
                    "insurers": insurers_count,
                    "cancer_types": cancer_types_count,
                    "stages": stages_count,
                    "hospital_tiers": tiers_count,
                    "base_costs": base_costs_count,
                    "accommodation_costs": accommodation_count
                }
            }
        except Exception as e:
            logger.error(f"Error seeding database: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")
    
    return router
