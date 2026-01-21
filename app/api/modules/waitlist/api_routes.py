"""
API routes for Medical Tourism Waitlist
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import MedicalTourismWaitlistRequest, MedicalTourismWaitlistResponse
from .service import WaitlistService
from typing import Optional
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Import auth service for user verification
auth_path = Path(__file__).parent.parent / "auth"
sys.path.insert(0, str(auth_path))
from app.api.modules.auth.service import AuthService


def create_api_router(db):
    """
    Create and return the API router for medical tourism waitlist.
    """
    router = APIRouter(prefix="/api/waitlist", tags=["waitlist"])
    waitlist_service = WaitlistService(db)
    auth_service = AuthService(db)
    
    def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
        """Get current user ID if authenticated"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        if payload:
            return payload.get("sub")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    @router.post("/medical-tourism", response_model=MedicalTourismWaitlistResponse, status_code=status.HTTP_201_CREATED)
    async def join_medical_tourism_waitlist(
        request: MedicalTourismWaitlistRequest,
        user_id: str = Depends(get_current_user_id)
    ):
        """Join the medical tourism waitlist"""
        try:
            # Add user_id to request data
            waitlist_data = request.model_dump()
            waitlist_data["user_id"] = user_id
            
            result = await waitlist_service.add_to_waitlist(waitlist_data)
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding to waitlist: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to join waitlist"
            )
    
    return router

