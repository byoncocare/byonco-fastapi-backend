"""
Payment service for RazorPay integration
"""
import os
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Try to import razorpay - with better error handling
try:
    import razorpay
    logger.info("✅ Razorpay package imported successfully")
except ImportError as e:
    razorpay = None
    logger.error(f"❌ Razorpay package import failed: {e}")
    logger.error("Please ensure 'razorpay' is installed: pip install razorpay")
    # Will be handled in service initialization

# Cache for the client (lazy initialization)
_razorpay_client_cache = None


def get_razorpay_client():
    """
    Lazy initialization of Razorpay client.
    Creates the client on demand and caches it.
    Raises ValueError if client cannot be initialized (route handler will convert to HTTPException).
    """
    global _razorpay_client_cache
    
    # Return cached client if available
    if _razorpay_client_cache is not None:
        return _razorpay_client_cache
    
    # Check if razorpay package is available
    if razorpay is None:
        logger.error("Razorpay package not installed")
        raise ValueError("Razorpay package not installed. Please install razorpay package.")
    
    # Read environment variables EXACTLY
    key_id = os.getenv("RAZORPAY_KEY_ID", "")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    # Strip whitespace
    key_id = key_id.strip() if key_id else ""
    key_secret = key_secret.strip() if key_secret else ""
    
    # Validate that both are present and non-empty
    if not key_id:
        logger.error("RAZORPAY_KEY_ID is missing or empty")
        raise ValueError("RAZORPAY_KEY_ID environment variable is not set or is empty")
    
    if not key_secret:
        logger.error("RAZORPAY_KEY_SECRET is missing or empty")
        raise ValueError("RAZORPAY_KEY_SECRET environment variable is not set or is empty")
    
    # Create and cache the client
    try:
        _razorpay_client_cache = razorpay.Client(auth=(key_id, key_secret))
        logger.info(f"Razorpay init ok: key_id_len={len(key_id)}, secret_len={len(key_secret)}")
        return _razorpay_client_cache
    except Exception as e:
        logger.error(f"Failed to initialize Razorpay client: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to initialize Razorpay client: {str(e)}")


class PaymentService:
    """Service for payment operations"""
    
    def __init__(self, db):
        self.db = db
        self.payments_collection = db.payments
    
    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[dict] = None) -> Dict[str, Any]:
        """Create RazorPay order"""
        # Get client lazily (will raise ValueError if not available)
        client = get_razorpay_client()
        
        if not receipt:
            receipt = f"receipt_{secrets.token_urlsafe(8)}"
        
        try:
            order_data = {
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {}
            }
            
            logger.info(f"Creating Razorpay order: amount={amount}, currency={currency}, receipt={receipt}")
            order = client.order.create(data=order_data)
            logger.info(f"Razorpay order created successfully: order_id={order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"Error creating RazorPay order: {str(e)}", exc_info=True)
            # Re-raise as ValueError so route handler can convert to HTTPException
            raise ValueError(f"Failed to create Razorpay order: {str(e)}")
    
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify RazorPay payment signature"""
        # Read secret directly from env (for signature verification)
        key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
        
        if not key_secret:
            logger.error("RAZORPAY_KEY_SECRET is missing for signature verification")
            raise ValueError("RazorPay key secret not configured")
        
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, razorpay_signature)
    
    async def save_payment(self, order_id: str, amount: float, currency: str, user_id: Optional[str] = None, service_type: Optional[str] = None) -> Dict[str, Any]:
        """Save payment record to database"""
        payment_doc = {
            "id": secrets.token_urlsafe(16),
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "user_id": user_id,
            "service_type": service_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.payments_collection.insert_one(payment_doc)
        return payment_doc
    
    async def update_payment_status(self, order_id: str, status: str, razorpay_payment_id: Optional[str] = None) -> bool:
        """Update payment status"""
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if razorpay_payment_id:
            update_data["razorpay_payment_id"] = razorpay_payment_id
        
        result = await self.payments_collection.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def get_payment_by_order_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by order ID"""
        payment = await self.payments_collection.find_one({"order_id": order_id})
        if payment:
            return dict(payment)
        return None
