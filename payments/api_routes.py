"""
API routes for Payment/RazorPay
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import PaymentRequest, PaymentVerification, PaymentResponse, RazorPayOrderResponse
from .service import PaymentService
import sys
from pathlib import Path
auth_path = Path(__file__).parent.parent / "auth"
sys.path.insert(0, str(auth_path))
from auth.service import AuthService
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def create_api_router(db):
    """
    Create and return the API router for payments.
    """
    router = APIRouter(prefix="/api/payments", tags=["payments"])
    payment_service = PaymentService(db)
    auth_service = AuthService(db)
    
    def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
        """Get current user ID if authenticated"""
        if not credentials:
            return None
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    @router.post("/create-order", response_model=RazorPayOrderResponse)
    async def create_payment_order(
        payment_request: PaymentRequest,
        user_id: Optional[str] = Depends(get_current_user_id)
    ):
        """Create RazorPay order"""
        try:
            # Create order in RazorPay
            order = payment_service.create_order(
                amount=payment_request.amount,
                currency=payment_request.currency,
                notes={
                    "description": payment_request.description,
                    "service_type": payment_request.service_type or "",
                    "user_id": user_id or ""
                }
            )
            
            # Save payment record
            await payment_service.save_payment(
                order_id=order["id"],
                amount=payment_request.amount,
                currency=payment_request.currency,
                user_id=user_id,
                service_type=payment_request.service_type
            )
            
            return {
                "order_id": order["id"],
                "amount": payment_request.amount,
                "currency": payment_request.currency,
                "receipt": order.get("receipt", ""),
                "status": order.get("status", "created")
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating payment order: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment order"
            )
    
    @router.post("/verify")
    async def verify_payment(verification: PaymentVerification):
        """Verify RazorPay payment"""
        try:
            # Verify signature
            is_valid = payment_service.verify_payment(
                razorpay_order_id=verification.razorpay_order_id,
                razorpay_payment_id=verification.razorpay_payment_id,
                razorpay_signature=verification.razorpay_signature
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payment signature"
                )
            
            # Update payment status
            await payment_service.update_payment_status(
                order_id=verification.razorpay_order_id,
                status="success",
                razorpay_payment_id=verification.razorpay_payment_id
            )
            
            return {
                "success": True,
                "message": "Payment verified successfully",
                "order_id": verification.razorpay_order_id,
                "payment_id": verification.razorpay_payment_id
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify payment"
            )
    
    @router.get("/order/{order_id}", response_model=PaymentResponse)
    async def get_payment_status(order_id: str):
        """Get payment status by order ID"""
        try:
            payment = await payment_service.get_payment_by_order_id(order_id)
            if not payment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment not found"
                )
            return payment
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get payment status"
            )
    
    return router

