"""
AI API Routes for ByOnco
Secure proxy endpoints for OpenAI API calls
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from .models import BuilderRequest, BuilderResponse, SecondOpinionRequest, SecondOpinionResponse
from .service import AIService

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Initialize AI service
ai_service = AIService()


def create_api_router():
    """
    Create and return the API router for AI endpoints.
    """
    router = APIRouter(prefix="/api/ai", tags=["ai"])

    @router.post("/builder", response_model=BuilderResponse)
    async def ai_builder(request: BuilderRequest):
        """
        Generate treatment plans using AI.
        Proxies to OpenAI API with backend key.
        """
        logger.info(f"[AI Builder] Request received - prompt length: {len(request.prompt)}, city: {request.city}, budget_max: {request.budget_max}")
        try:
            result = await ai_service.generate_builder_plans(
                prompt=request.prompt,
                city=request.city,
                budget_max=request.budget_max,
                context=request.context,
            )
            logger.info(f"[AI Builder] Request completed successfully")
            return BuilderResponse(**result)
        except Exception as e:
            logger.error(f"[AI Builder] Error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate treatment plans"
            )

    @router.post("/second-opinion", response_model=SecondOpinionResponse)
    async def ai_second_opinion(
        request: SecondOpinionRequest,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ):
        """
        Generate second opinion using AI.
        - Validates health-related questions
        - Enforces daily limits (2 free/day)
        - Returns paywall info if limit exceeded
        """
        logger.info(f"[AI Second Opinion] Request received - question length: {len(request.question) if request.question else 0}, attachments: {len(request.attachments) if request.attachments else 0}")
        try:
            # TODO: Get user_id from JWT token and check daily limit
            # For now, skip daily limit check (will be added in next step)
            
            result = await ai_service.generate_second_opinion(
                question=request.question,
                attachments=request.attachments,
                profile=request.profile,
            )

            # If validation failed, return error
            if not result.get("safe", True):
                logger.warning(f"[AI Second Opinion] Validation failed: {result.get('error', 'Invalid question')}")
                return SecondOpinionResponse(
                    answer=None,
                    safe=False,
                    error=result.get("error", "Invalid question"),
                )

            # TODO: Check daily limit from Supabase
            # If limit exceeded, return paywall response
            # For now, always return answer

            paywall_required = result.get("paywall_required", False)
            if paywall_required:
                logger.info(f"[AI Second Opinion] Paywall required - daily limit exceeded")
            else:
                logger.info(f"[AI Second Opinion] Request completed successfully")

            return SecondOpinionResponse(
                answer=result.get("answer"),
                safe=True,
                paywall_required=paywall_required,
                amount_inr=result.get("amount_inr"),
                error=result.get("error"),
            )
        except Exception as e:
            logger.error(f"[AI Second Opinion] Error: {e}", exc_info=True)
            return SecondOpinionResponse(
                answer=None,
                safe=True,
                error=f"Failed to generate second opinion: {str(e)}"
            )

    return router


