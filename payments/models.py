"""
Pydantic models for Payment/RazorPay integration
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentRequest(BaseModel):
    """Payment creation request"""
    amount: float = Field(..., gt=0, description="Amount in INR")
    currency: str = Field(default="INR", description="Currency code")
    description: str = Field(..., description="Payment description")
    service_type: Optional[str] = None  # e.g., "second_opinion", "teleconsultation", "cost_calculator"
    metadata: Optional[dict] = None


class RazorPayOrderResponse(BaseModel):
    """RazorPay order response"""
    order_id: str
    amount: float
    currency: str
    receipt: str
    status: str


class PaymentVerification(BaseModel):
    """Payment verification request"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    amount: float


class PaymentResponse(BaseModel):
    """Payment response model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    order_id: str
    amount: float
    currency: str
    status: PaymentStatus
    razorpay_payment_id: Optional[str] = None
    user_id: Optional[str] = None
    service_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime








