"""
API routes for Payment/RazorPay
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import PaymentRequest, PaymentVerification, PaymentResponse, RazorPayOrderResponse
from .service import PaymentService
import sys
import os
import uuid
from pathlib import Path
auth_path = Path(__file__).parent.parent / "auth"
sys.path.insert(0, str(auth_path))
from auth.service import AuthService
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Note: RAZORPAY_KEY_ID is now read directly from env when needed
# No global initialization to avoid silent failures


def create_api_router(db):
    """
    Create and return the API router for payments.
    """
    router = APIRouter(prefix="/api/payments", tags=["payments"])
    razorpay_router = APIRouter(prefix="/api/payments/razorpay", tags=["razorpay"])
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
    
    # Vayu-specific Razorpay endpoints (matches frontend expectations)
    @razorpay_router.post("/create-order")
    async def create_vayu_order(
        request_data: dict = Body(...),
        user_id: Optional[str] = Depends(get_current_user_id)
    ):
        """Create RazorPay order for Vayu checkout (accepts cart format)"""
        try:
            # Extract amount from cart
            cart = request_data.get("cart", {})
            items = cart.get("items", [])
            if not items:
                raise HTTPException(status_code=400, detail="Cart is empty")
            
            # Calculate total from cart items
            total = sum(item.get("unitPrice", 0) * item.get("quantity", 1) for item in items)
            
            # Apply coupon if provided
            coupon_code = request_data.get("couponCode", "")
            if coupon_code:
                # Simple coupon logic (10% off for LAUNCH2025, 5000 off for VAYU5000)
                normalized = coupon_code.strip().upper()
                if normalized == "LAUNCH2025":
                    total = total * 0.9
                elif normalized == "VAYU5000":
                    total = max(0, total - 5000)
            
            # Create order in RazorPay
            order = payment_service.create_order(
                amount=total,
                currency="INR",
                notes={
                    "description": "Vayu AI Glasses",
                    "service_type": "vayu_order",
                    "user_id": user_id or "",
                    "cart": str(cart)
                }
            )
            
            # Generate internal order ID
            internal_order_id = str(uuid.uuid4())
            
            # Save payment record
            await payment_service.save_payment(
                order_id=order["id"],
                amount=total,
                currency="INR",
                user_id=user_id,
                service_type="vayu_order"
            )
            
            # Get key ID for response (read fresh from env)
            key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
            
            # Return format expected by Vayu frontend
            return {
                "keyId": key_id,
                "razorpayOrderId": order["id"],
                "orderId": internal_order_id,
                "amount": total,
                "currency": "INR"
            }
        except HTTPException:
            # Re-raise HTTPException as-is (from other HTTP errors)
            raise
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"ValueError creating Vayu order: {error_msg}", exc_info=True)
            # Check if it's an initialization error (500) or validation error (400)
            if "environment variable" in error_msg or "not installed" in error_msg or "Failed to initialize" in error_msg:
                raise HTTPException(status_code=500, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        except Exception as e:
            logger.error(f"Error creating Vayu order: {str(e)}", exc_info=True)
            # Preserve the actual error message for debugging
            error_detail = str(e) if str(e) else "Failed to create order"
            raise HTTPException(status_code=500, detail=error_detail)
    
    @razorpay_router.post("/verify")
    async def verify_vayu_payment(verification_data: dict = Body(...)):
        """Verify RazorPay payment for Vayu (accepts frontend format)"""
        try:
            razorpay_order_id = verification_data.get("razorpayOrderId")
            razorpay_payment_id = verification_data.get("razorpayPaymentId")
            razorpay_signature = verification_data.get("razorpaySignature")
            internal_order_id = verification_data.get("internalOrderId")
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                raise HTTPException(status_code=400, detail="Missing payment verification data")
            
            # Verify signature (reads secret from env directly)
            is_valid = payment_service.verify_payment(
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature
            )
            
            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid payment signature")
            
            # Update payment status
            await payment_service.update_payment_status(
                order_id=razorpay_order_id,
                status="success",
                razorpay_payment_id=razorpay_payment_id
            )
            
            return {
                "success": True,
                "message": "Payment verified successfully",
                "orderId": internal_order_id or razorpay_order_id,
                "payment_id": razorpay_payment_id
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying Vayu payment: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to verify payment")
    
    @razorpay_router.get("/key")
    async def get_razorpay_key():
        """Get Razorpay key ID (public key only, safe to expose)"""
        key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
        if not key_id:
            raise HTTPException(
                status_code=500,
                detail="Razorpay key not configured"
            )
        return {"keyId": key_id}
    
    @razorpay_router.get("/health")
    async def razorpay_health():
        """Health check endpoint for Razorpay configuration"""
        import os
        key_id_present = bool(os.getenv("RAZORPAY_KEY_ID", ""))
        key_secret_present = bool(os.getenv("RAZORPAY_KEY_SECRET", ""))
        
        return {
            "ok": True,
            "key_id_present": key_id_present,
            "key_secret_present": key_secret_present
        }
    
    @razorpay_router.get("/env-check")
    async def razorpay_env_check():
        """Diagnostic endpoint for Razorpay environment variables (safe - no secrets)"""
        import os
        import subprocess
        
        # Check if razorpay package is installed
        razorpay_installed = False
        razorpay_version = "unknown"
        razorpay_error = None
        try:
            import razorpay
            razorpay_installed = True
            try:
                razorpay_version = razorpay.__version__
            except:
                razorpay_version = "installed (version unknown)"
        except ImportError as e:
            razorpay_installed = False
            razorpay_error = str(e)
            razorpay_version = f"not installed: {razorpay_error}"
        
        key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
        key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
        
        # Get git commit hash if available
        service_version = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2,
                cwd=Path(__file__).parent.parent.parent
            )
            if result.returncode == 0:
                service_version = result.stdout.strip()
        except Exception:
            pass  # Ignore if git is not available
        
        return {
            "razorpay_installed": razorpay_installed,
            "razorpay_version": razorpay_version,
            "razorpay_error": razorpay_error,
            "key_id_present": bool(key_id),
            "key_secret_present": bool(key_secret),
            "key_id_len": len(key_id),
            "key_secret_len": len(key_secret),
            "key_id_prefix": key_id[:6] if len(key_id) >= 6 else "",
            "key_id_suffix": key_id[-4:] if len(key_id) >= 4 else "",
            "service_version": service_version
        }
    
    return router, razorpay_router

