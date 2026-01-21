"""
API routes for Get Started form
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import GetStartedRequest, GetStartedResponse
from .service import GetStartedService
import sys
from pathlib import Path
auth_path = Path(__file__).parent.parent / "auth"
sys.path.insert(0, str(auth_path))
from app.api.modules.auth.service import AuthService
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def create_api_router(db):
    """
    Create and return the API router for Get Started form.
    """
    router = APIRouter(prefix="/api/get-started", tags=["get-started"])
    service = GetStartedService(db)
    auth_service = AuthService(db)
    
    def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
        """Get current user ID if authenticated (for admin access)"""
        if not credentials:
            return None
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    @router.post("/submit", response_model=GetStartedResponse, status_code=status.HTTP_201_CREATED)
    async def submit_get_started(request: GetStartedRequest):
        """Submit Get Started form"""
        try:
            # Validate required fields
            if not request.agree_to_terms:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You must agree to terms and conditions"
                )
            
            result = await service.create_submission(request)
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit form. Please try again."
            )
    
    @router.get("/submissions", response_model=List[dict])
    async def get_submissions(
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=1000),
        user_id: Optional[str] = Depends(get_current_user_id)
    ):
        """Get all submissions (Admin only - requires authentication)"""
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        try:
            submissions = await service.get_all_submissions(status=status, limit=limit)
            return submissions
        except Exception as e:
            logger.error(f"Error getting submissions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get submissions"
            )
    
    @router.get("/submission/{submission_id}", response_model=dict)
    async def get_submission(
        submission_id: str,
        user_id: Optional[str] = Depends(get_current_user_id)
    ):
        """Get a specific submission (Admin only)"""
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        try:
            submission = await service.get_submission(submission_id)
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Submission not found"
                )
            return submission
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting submission: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get submission"
            )
    
    return router

