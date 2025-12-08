"""
Payment service for RazorPay integration
"""
try:
    import razorpay
except ImportError:
    razorpay = None
    # Will be handled in service initialization
import os
import hmac
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# RazorPay credentials (should be in .env)
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

# Initialize RazorPay client
razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class PaymentService:
    """Service for payment operations"""
    
    def __init__(self, db):
        self.db = db
        self.payments_collection = db.payments
        self.client = razorpay_client
    
    def create_order(self, amount: float, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[dict] = None) -> Dict[str, Any]:
        """Create RazorPay order"""
        if not self.client:
            raise ValueError("RazorPay client not initialized. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment variables.")
        
        if not receipt:
            receipt = f"receipt_{secrets.token_urlsafe(8)}"
        
        try:
            order_data = {
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "receipt": receipt,
                "notes": notes or {}
            }
            
            order = self.client.order.create(data=order_data)
            return order
        except Exception as e:
            logger.error(f"Error creating RazorPay order: {str(e)}")
            raise
    
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify RazorPay payment signature"""
        if not RAZORPAY_KEY_SECRET:
            raise ValueError("RazorPay key secret not configured")
        
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
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

