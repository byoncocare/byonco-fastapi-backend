"""
API routes for Rare Cancers feature
"""
from fastapi import APIRouter, HTTPException, Query
from .models import RareCancer, RareCancerDetail
from .service import RareCancersService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def create_api_router():
    """
    Create and return the API router for rare cancers.
    Similar structure to cost_calculator/api_routes.py
    """
    router = APIRouter(prefix="/api/rare-cancers", tags=["rare-cancers"])
    service = RareCancersService()
    
    @router.get("", response_model=List[RareCancer])
    async def get_all_rare_cancers(
        category: Optional[str] = Query(None, description="Filter by category: ultra-rare, very-rare, rare")
    ):
        """Get all rare cancers with optional filtering by category"""
        try:
            cancers = service.get_all_rare_cancers(category=category)
            return cancers
        except Exception as e:
            logger.error(f"Error fetching rare cancers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch rare cancers")
    
    @router.get("/{cancer_name}", response_model=RareCancerDetail)
    async def get_rare_cancer_detail(cancer_name: str):
        """Get detailed information about a specific rare cancer"""
        try:
            cancer = service.get_rare_cancer_by_name(cancer_name)
            if not cancer:
                raise HTTPException(status_code=404, detail="Rare cancer not found")
            return cancer
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching rare cancer details: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch rare cancer details")
    
    @router.get("/category/{category}", response_model=List[RareCancer])
    async def get_cancers_by_category(category: str):
        """Get all cancers in a specific category"""
        try:
            if category not in ["ultra-rare", "very-rare", "rare"]:
                raise HTTPException(status_code=400, detail="Invalid category. Must be: ultra-rare, very-rare, or rare")
            cancers = service.get_cancers_by_category(category)
            return cancers
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching cancers by category: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch cancers by category")
    
    @router.get("/search/{query}", response_model=List[RareCancer])
    async def search_rare_cancers(query: str):
        """Search rare cancers by name or type"""
        try:
            results = service.search_rare_cancers(query)
            return results
        except Exception as e:
            logger.error(f"Error searching rare cancers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to search rare cancers")
    
    @router.get("/{cancer_name}/specialists")
    async def get_specialists_for_cancer(cancer_name: str):
        """
        Get specialist oncologists for a given rare cancer.
        Returns a simple JSON list, used by RareCancersPage and Find Oncologists.
        """
        try:
            # Decode URL-encoded cancer name
            from urllib.parse import unquote
            decoded_name = unquote(cancer_name)
            logger.info(f"=== Fetching specialists for cancer: '{decoded_name}' ===")
            logger.info(f"Total cancer types with specialists: {len(service.rare_cancer_specialists)}")
            logger.info(f"Sample keys: {list(service.rare_cancer_specialists.keys())[:3]}")
            
            specialists = service.get_specialists_for_cancer(decoded_name)
            
            # Try alternative name matching if exact match fails
            if not specialists:
                logger.warning(f"No exact match found, trying case-insensitive matching...")
                # Try case-insensitive matching
                for key in service.rare_cancer_specialists.keys():
                    if key.lower().strip() == decoded_name.lower().strip():
                        specialists = service.get_specialists_for_cancer(key)
                        logger.info(f"Found specialists using case-insensitive match: '{key}'")
                        break
            
            # Return empty array instead of 404 if no specialists found
            logger.info(f"=== Returning {len(specialists)} specialists for '{decoded_name}' ===")
            if specialists:
                logger.info(f"Sample specialist: {specialists[0].get('name', 'N/A')}")
            return specialists if specialists else []
        except Exception as e:
            logger.error(f"Error fetching specialists for {cancer_name}: {str(e)}")
            logger.exception(e)  # Log full traceback
            # Return empty array on error instead of raising exception
            return []
    
    @router.get("/specialists/test")
    async def test_specialists():
        """Test endpoint to verify specialists data is loaded"""
        try:
            rare_total = sum(len(specs) for specs in service.rare_cancer_specialists.values())
            common_total = sum(len(specs) for specs in service.common_cancer_specialists.values())
            total_specialists = rare_total + common_total
            rare_types = list(service.rare_cancer_specialists.keys())
            common_types = list(service.common_cancer_specialists.keys())
            all_types = rare_types + common_types
            return {
                "total_specialists": total_specialists,
                "rare_cancer_specialists": rare_total,
                "common_cancer_specialists": common_total,
                "rare_cancer_types": len(rare_types),
                "common_cancer_types": len(common_types),
                "total_cancer_types": len(all_types),
                "sample_rare_cancer_types": rare_types[:3],
                "sample_common_cancer_types": common_types[:3],
                "sample_rare_specialists": service.rare_cancer_specialists.get("Diffuse Intrinsic Pontine Glioma (DIPG)", [])[:2],
                "sample_common_specialists": service.common_cancer_specialists.get("Breast Cancer", [])[:2]
            }
        except Exception as e:
            logger.error(f"Error in test endpoint: {str(e)}")
            return {"error": str(e)}
    
    @router.get("/specialists")
    async def get_all_specialists(
        name: Optional[str] = Query(None, description="Filter by doctor name (contains)"),
        cancer_name: Optional[str] = Query(None, description="Filter by cancer name (contains)"),
        region: Optional[str] = Query(None, description="Filter by region: USA, Singapore, Europe, India"),
        min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    ):
        """
        Flattened list of all specialists, used by the Find Oncologists page.
        """
        try:
            docs = service.get_all_specialists(
                name=name,
                cancer_name=cancer_name,
                region=region,
                min_experience=min_experience,
            )
            return docs
        except Exception as e:
            logger.error(f"Error fetching specialists: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch specialists")
    
    return router
