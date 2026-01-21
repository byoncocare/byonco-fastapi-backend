"""
API routes for Journey Builder
"""
from fastapi import APIRouter, HTTPException
from .models import JourneyRequest, JourneyResponse
from .service import JourneyBuilderService
import logging

logger = logging.getLogger(__name__)


def create_api_router():
    """
    Create and return the API router for journey builder.
    """
    router = APIRouter(prefix="/api/journey-builder", tags=["journey-builder"])
    
    try:
        journey_service = JourneyBuilderService()
    except ValueError as e:
        logger.error(f"Failed to initialize JourneyBuilderService: {e}")
        journey_service = None
    
    @router.post("/", response_model=JourneyResponse)
    async def build_journey(request: JourneyRequest):
        """
        Build a medical journey plan based on user's free-text description.
        
        This endpoint uses OpenAI GPT-4o to:
        - Extract journey profile (cancer type, stage, origin/destination, budget)
        - Generate 3 journey packages (Value, Balanced, Comfort)
        - Provide optimization suggestions
        """
        if not journey_service:
            raise HTTPException(
                status_code=500,
                detail="Journey Builder service is not available. Please check OPENAI_API_KEY configuration."
            )
        
        try:
            result = await journey_service.build_journey(request.message)
            
            # Validate that we have the required structure
            if not result.get("profile") or not result.get("plans"):
                logger.warning("OpenAI returned incomplete response structure")
                raise HTTPException(
                    status_code=500,
                    detail="Received incomplete response from AI service. Please try again."
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error building journey: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build journey plan: {str(e)}"
            )
    
    return router

