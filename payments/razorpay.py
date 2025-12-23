"""
Razorpay Payment Integration for Vayu Orders
============================================

This module provides secure Razorpay payment endpoints for Vayu AI Glasses orders.

Security:
- All pricing is calculated server-side (client prices are ignored)
- Payment signatures are verified using HMAC-SHA256
- RAZORPAY_KEY_SECRET is never exposed to clients
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import os
import hmac
import hashlib
import secrets
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# Import Razorpay SDK with alias to avoid naming collisions
try:
    import razorpay as razorpay_sdk
except ImportError as e:
    # Check if it's a missing dependency (like pkg_resources/setuptools)
    if "pkg_resources" in str(e) or "setuptools" in str(e):
        raise ImportError(
            "razorpay package dependencies missing. Install with: pip install setuptools razorpay"
        ) from e
    raise ImportError(
        "razorpay package not installed. Install with: pip install razorpay"
    ) from e
except ModuleNotFoundError as e:
    # Handle ModuleNotFoundError (Python 3.6+)
    if "pkg_resources" in str(e) or "setuptools" in str(e):
        raise ImportError(
            "razorpay package dependencies missing. Install with: pip install setuptools razorpay"
        ) from e
    raise ImportError(
        "razorpay package not installed. Install with: pip install razorpay"
    ) from e

router = APIRouter(prefix="/api/payments/razorpay", tags=["Razorpay"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Razorpay configuration.
    Returns whether RAZORPAY_KEY_ID is configured (never returns secret).
    """
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    return {
        "status": "ok",
        "razorpay_configured": bool(key_id and key_secret),
        "key_id_present": bool(key_id),
        # Never return key_secret or key_id value
    }


def _get_razorpay_client():
    """
    Helper function to safely create Razorpay client.
    Loads environment variables and validates they exist.
    
    Returns:
        razorpay_sdk.Client: Initialized Razorpay client
        
    Raises:
        ValueError: If environment variables are not set
    """
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        raise ValueError(
            "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in environment variables"
        )
    
    return razorpay_sdk.Client(auth=(key_id, key_secret))


def _get_key_id():
    """Get RAZORPAY_KEY_ID from environment (public key only)."""
    key_id = os.getenv("RAZORPAY_KEY_ID")
    if not key_id:
        raise ValueError("RAZORPAY_KEY_ID must be set in environment variables")
    return key_id


def _get_key_secret():
    """Get RAZORPAY_KEY_SECRET from environment (for signature verification only)."""
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_secret:
        raise ValueError("RAZORPAY_KEY_SECRET must be set in environment variables")
    return key_secret

# ============================================================================
# SERVER-SIDE PRODUCT CATALOG (Canonical Pricing Source)
# ============================================================================

VAYU_PRODUCT_CATALOG = {
    "vayu-ai-glasses": {
        "name": "Vayu AI Glasses",
        "base_price": 59999.0,  # INR - Non-prescription base price
        "variants": {
            "non-prescription": {
                "label": "Non-prescription",
                "price_delta": 0,
                "compare_at_price": 69999.0,
            },
            "prescription": {
                "label": "Prescription",
                "price_delta": 5000,  # Additional ₹5,000
                "compare_at_price": 74999.0,
            },
        },
        "max_quantity": 5,
    }
}


def get_unit_price(product_id: str, variant_id: str) -> float:
    """Get unit price for a product variant (server-side calculation)."""
    if product_id not in VAYU_PRODUCT_CATALOG:
        raise ValueError(f"Unknown product: {product_id}")

    product = VAYU_PRODUCT_CATALOG[product_id]
    if variant_id not in product["variants"]:
        raise ValueError(f"Unknown variant: {variant_id} for product {product_id}")

    variant = product["variants"][variant_id]
    return product["base_price"] + variant["price_delta"]


def validate_quantity(product_id: str, quantity: int) -> None:
    """Validate quantity is within allowed range."""
    if product_id not in VAYU_PRODUCT_CATALOG:
        raise ValueError(f"Unknown product: {product_id}")

    max_qty = VAYU_PRODUCT_CATALOG[product_id]["max_quantity"]
    if quantity < 1 or quantity > max_qty:
        raise ValueError(f"Quantity must be between 1 and {max_qty}")


def apply_coupon(subtotal: float, coupon_code: Optional[str]) -> tuple[float, float]:
    """
    Apply coupon discount (server-side calculation).
    Returns: (discount_amount, final_amount)
    """
    if not coupon_code:
        return 0.0, subtotal

    coupon_code = coupon_code.strip().upper()

    if coupon_code == "LAUNCH2025":
        discount = round(subtotal * 0.10, 2)  # 10% off
        return discount, subtotal - discount
    elif coupon_code == "VAYU5000":
        discount = min(5000.0, subtotal)  # Flat ₹5,000 off (max discount = subtotal)
        return discount, subtotal - discount

    raise ValueError("Invalid coupon code")


def calculate_order_totals(
    product_id: str, variant_id: str, quantity: int, coupon_code: Optional[str] = None
) -> dict:
    """
    Calculate order totals server-side (canonical pricing logic).
    Returns dict with: subtotal, discount, final_total, total_paise
    """
    # Validate inputs
    validate_quantity(product_id, quantity)
    unit_price = get_unit_price(product_id, variant_id)

    # Calculate subtotal
    subtotal = unit_price * quantity

    # Apply coupon
    discount, final_total = apply_coupon(subtotal, coupon_code)

    # Shipping is free for now
    shipping_cost = 0.0

    # Final total
    total = final_total + shipping_cost

    # Convert to paise for Razorpay (amount must be in smallest currency unit)
    total_paise = int(round(total * 100))

    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping_cost,
        "final_total": total,
        "total_paise": total_paise,
        "unit_price": unit_price,
    }


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CartItem(BaseModel):
    productId: Optional[str] = None
    name: Optional[str] = None
    variantId: Optional[str] = None
    variantLabel: Optional[str] = None
    quantity: Optional[int] = None
    unitPrice: Optional[float] = None
    compareAtPrice: Optional[float] = None
    image: Optional[str] = None

class Cart(BaseModel):
    items: Optional[List[CartItem]] = []
    currency: Optional[str] = "INR"

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

class ShippingAddress(BaseModel):
    country: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin: Optional[str] = None

class CreateOrderRequest(BaseModel):
    # Support both formats: direct fields (for curl/testing) and cart structure (from frontend)
    productId: Optional[str] = Field(None, description="Product ID (e.g., 'vayu-ai-glasses')")
    variantId: Optional[str] = Field(None, description="Variant ID (e.g., 'non-prescription' or 'prescription')")
    quantity: Optional[int] = Field(None, gt=0, description="Quantity (1-5)")
    couponCode: Optional[str] = Field(None, description="Optional coupon code")
    customer: Optional[CustomerInfo] = Field(None, description="Optional customer info")
    # Frontend format
    cart: Optional[Cart] = Field(None, description="Cart object from frontend")
    contact: Optional[ContactInfo] = Field(None, description="Contact info from frontend")
    shippingAddress: Optional[ShippingAddress] = Field(None, description="Shipping address from frontend")


class CreateOrderResponse(BaseModel):
    orderId: str  # Internal order ID (e.g., "VAYU-2025-ABC123")
    razorpayOrderId: str  # Razorpay order ID (e.g., "order_ABC123XYZ")
    amount: float  # Final amount in INR (not paise)
    currency: str
    keyId: str  # Public key ID only


class VerifyPaymentRequest(BaseModel):
    # Support both naming conventions (snake_case from curl, camelCase from frontend)
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    razorpayOrderId: Optional[str] = None
    razorpayPaymentId: Optional[str] = None
    razorpaySignature: Optional[str] = None
    internalOrderId: Optional[str] = None  # For reference only


class VerifyPaymentResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(request: CreateOrderRequest):
    """
    Create a Razorpay order with server-side pricing calculation.

    SECURITY:
    - All pricing is calculated server-side (client prices are ignored)
    - Product ID and variant are validated
    - Quantity is validated against max allowed
    - Coupon codes are validated server-side
    
    Supports two request formats:
    1. Direct fields (for testing): productId, variantId, quantity, couponCode
    2. Cart structure (from frontend): cart.items[0], couponCode
    """
    try:
        # Extract product info from either format
        if request.cart and request.cart.items and len(request.cart.items) > 0:
            # Frontend format: extract from cart
            item = request.cart.items[0]
            product_id = item.productId or "vayu-ai-glasses"
            variant_id = item.variantId or "non-prescription"
            quantity = item.quantity or 1
            coupon_code = request.couponCode
        else:
            # Direct format (for curl/testing)
            product_id = request.productId or "vayu-ai-glasses"
            variant_id = request.variantId or "non-prescription"
            quantity = request.quantity or 1
            coupon_code = request.couponCode
        
        logger.info(
            f"Creating Razorpay order: product={product_id}, "
            f"variant={variant_id}, quantity={quantity}, "
            f"coupon={coupon_code or 'none'}"
        )
        
        # Server-side pricing calculation (IGNORE any client-provided prices)
        totals = calculate_order_totals(
            product_id=product_id,
            variant_id=variant_id,
            quantity=quantity,
            coupon_code=coupon_code,
        )

        # Generate unique order ID
        order_id = f"VAYU-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"

        logger.info(f"Order {order_id}: calculated total={totals['final_total']} INR ({totals['total_paise']} paise)")

        # Create Razorpay order
        try:
            client = _get_razorpay_client()
            razorpay_order = client.order.create(
                {
                    "amount": totals["total_paise"],  # Amount in paise
                    "currency": "INR",
                    "receipt": f"vayu_{order_id}",
                    "notes": {
                        "internal_order_id": order_id,
                        "product": product_id,
                        "variant": variant_id,
                        "quantity": str(quantity),
                    },
                }
            )
            razorpay_order_id = razorpay_order.get("id", "")
            logger.info(f"Order {order_id}: Razorpay order created successfully, razorpay_order_id={razorpay_order_id}")
        except ValueError as e:
            # Environment variable error
            logger.error(f"Order {order_id}: Configuration error - {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Payment service configuration error. Please contact support."
            )
        except Exception as e:
            # Log error but don't expose internal details
            logger.error(f"Order {order_id}: Razorpay API error - {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create payment order. Please try again."
            )

        return CreateOrderResponse(
            orderId=order_id,
            razorpayOrderId=razorpay_order_id,
            amount=totals["final_total"],  # Return in INR (not paise)
            currency="INR",
            keyId=_get_key_id(),  # Public key only
        )

    except ValueError as e:
        logger.warning(f"Create order validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_order: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating your order. Please try again.",
        )


@router.post("/verify", response_model=VerifyPaymentResponse)
async def verify_payment(request: VerifyPaymentRequest):
    """
    Verify Razorpay payment signature.

    SECURITY:
    - Signature is verified using HMAC-SHA256
    - Constant-time comparison to prevent timing attacks
    - Only returns success if signature is valid
    """
    try:
        # Support both naming conventions (snake_case and camelCase)
        razorpay_order_id = request.razorpay_order_id or request.razorpayOrderId
        razorpay_payment_id = request.razorpay_payment_id or request.razorpayPaymentId
        razorpay_signature = request.razorpay_signature or request.razorpaySignature
        
        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            logger.error("Missing required payment verification fields")
            return VerifyPaymentResponse(
                ok=False, error="Missing required payment information"
            )
        
        logger.info(
            f"Verifying payment: razorpay_order_id={razorpay_order_id}, "
            f"razorpay_payment_id={razorpay_payment_id[:10]}..."
        )
        
        # Verify payment signature (CRITICAL SECURITY STEP)
        key_secret = _get_key_secret()
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            key_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(generated_signature, razorpay_signature):
            # Log failed verification attempt (for security monitoring)
            logger.warning(
                f"Payment signature verification failed for order {razorpay_order_id}"
            )
            return VerifyPaymentResponse(
                ok=False, error="Invalid payment signature"
            )

        # Signature is valid
        logger.info(f"Payment verified successfully: razorpay_order_id={razorpay_order_id}")
        # TODO: Store payment confirmation in database
        # TODO: Send order confirmation email

        return VerifyPaymentResponse(ok=True)

    except ValueError as e:
        logger.error(f"Payment verification configuration error: {str(e)}")
        return VerifyPaymentResponse(
            ok=False, error="Payment verification service error. Please contact support."
        )
    except Exception as e:
        logger.error(f"Unexpected error in verify_payment: {type(e).__name__}: {str(e)}")
        return VerifyPaymentResponse(
            ok=False, error="An error occurred while verifying payment."
        )

