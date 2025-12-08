from fastapi import APIRouter, HTTPException
from models import (
    Country, Insurer, CancerType, Stage, HospitalTier,
    CostCalculationRequest, CostCalculationResponse
)
from cost_calculator_service import CostCalculatorService
from typing import List
import logging

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
    
    return router
