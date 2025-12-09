"""
API routes for Authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import (
    UserRegister, UserLogin, GoogleAuthRequest,
    UserResponse, TokenResponse, PasswordResetRequest, PasswordResetConfirm,
    ProfileUpdate
)
from .service import AuthService
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


def create_api_router(db):
    """
    Create and return the API router for authentication.
    """
    router = APIRouter(prefix="/api/auth", tags=["authentication"])
    auth_service = AuthService(db)
    
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Dependency to get current authenticated user"""
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"user_id": user_id, "email": payload.get("email")}
    
    @router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
    async def register(user_data: UserRegister):
        """Register a new user"""
        try:
            if not user_data.agree_to_terms:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You must agree to terms and conditions"
                )
            
            user_doc = await auth_service.register_user(
                email=user_data.email,
                password=user_data.password,
                full_name=user_data.full_name,
                phone=user_data.phone
            )
            
            # Create token
            token_data = {"sub": user_doc["id"], "email": user_doc["email"]}
            access_token = auth_service.create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_doc
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @router.post("/login", response_model=TokenResponse)
    async def login(credentials: UserLogin):
        """Login user"""
        try:
            result = await auth_service.login_user(
                email=credentials.email,
                password=credentials.password
            )
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            return {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "user": result["user"]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @router.post("/google", response_model=TokenResponse)
    async def google_auth(auth_data: GoogleAuthRequest):
        """Google OAuth authentication"""
        try:
            result = await auth_service.google_auth(
                google_id_token=auth_data.id_token,
                full_name=auth_data.full_name,
                phone=auth_data.phone
            )
            return result
        except NotImplementedError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google authentication is not yet implemented. Please use email/password registration."
            )
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google authentication failed"
            )
    
    @router.get("/me", response_model=UserResponse)
    async def get_current_user_info(current_user: dict = Depends(get_current_user)):
        """Get current user information"""
        try:
            user = await auth_service.get_user_by_id(current_user["user_id"])
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user information"
            )
    
    @router.post("/forgot-password")
    async def forgot_password(request: PasswordResetRequest):
        """Request password reset"""
        try:
            token = await auth_service.create_password_reset_token(request.email)
            if token:
                # In production, send email with reset link
                # For now, just return success (don't expose token in production)
                return {"message": "If the email exists, a password reset link has been sent"}
            return {"message": "If the email exists, a password reset link has been sent"}
        except Exception as e:
            logger.error(f"Password reset request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process password reset request"
            )
    
    @router.post("/reset-password")
    async def reset_password(confirm: PasswordResetConfirm):
        """Reset password using token"""
        try:
            success = await auth_service.reset_password(
                token=confirm.token,
                new_password=confirm.new_password
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            return {"message": "Password reset successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )
    
    @router.put("/profile", response_model=UserResponse)
    async def update_profile(
        profile_data: ProfileUpdate,
        current_user: dict = Depends(get_current_user)
    ):
        """Update user profile"""
        try:
            # Convert Pydantic model to dict, excluding None values
            update_dict = profile_data.model_dump(exclude_none=True)
            
            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No profile data provided"
                )
            
            updated_user = await auth_service.update_user_profile(
                user_id=current_user["user_id"],
                profile_data=update_dict
            )
            
            if updated_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return updated_user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
    
    return router

