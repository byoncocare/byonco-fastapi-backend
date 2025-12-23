# Razorpay End-to-End Testing Guide

## Quick Start

### 1. Verify Server is Running
```bash
python -m uvicorn server:app --reload
```

Visit: `http://localhost:8000/docs` - Should show Razorpay endpoints

### 2. Check Health
```bash
curl http://localhost:8000/api/payments/razorpay/health
```

Expected:
```json
{
  "status": "ok",
  "razorpay_configured": true,
  "key_id_present": true
}
```

## CURL Commands

### Create Order (Non-prescription, No Coupon)
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "vayu-ai-glasses",
    "variantId": "non-prescription",
    "quantity": 1
  }'
```

**Response**:
```json
{
  "orderId": "VAYU-2025-ABC123",
  "razorpayOrderId": "order_xyz789",
  "amount": 59999.0,
  "currency": "INR",
  "keyId": "rzp_test_..."
}
```

### Create Order (Prescription, With Coupon)
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "vayu-ai-glasses",
    "variantId": "prescription",
    "quantity": 1,
    "couponCode": "LAUNCH2025"
  }'
```

**Response**:
```json
{
  "orderId": "VAYU-2025-XYZ789",
  "razorpayOrderId": "order_abc456",
  "amount": 58499.1,
  "currency": "INR",
  "keyId": "rzp_test_..."
}
```

### Verify Payment
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/verify \
  -H "Content-Type: application/json" \
  -d '{
    "razorpayOrderId": "order_ABC123XYZ",
    "razorpayPaymentId": "pay_DEF456UVW",
    "razorpaySignature": "abc123def456..."
  }'
```

**Success Response**:
```json
{
  "ok": true
}
```

**Failure Response**:
```json
{
  "ok": false,
  "error": "Invalid payment signature"
}
```

## Frontend Configuration

### Local Development
Create `.env.local` in frontend root:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Production
Set environment variable:
```bash
REACT_APP_BACKEND_URL=https://byonco-fastapi-backend.onrender.com
```

## Endpoints Summary

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/payments/razorpay/health` | GET | Health check | `{status, razorpay_configured, key_id_present}` |
| `/api/payments/razorpay/create-order` | POST | Create order | `{orderId, razorpayOrderId, amount, currency, keyId}` |
| `/api/payments/razorpay/verify` | POST | Verify payment | `{ok, error?}` |

## Security Notes

✅ All endpoints return JSON  
✅ No secrets exposed  
✅ User-friendly error messages  
✅ Server-side pricing calculation  
✅ Payment signature verification  

## Testing Checklist

- [x] Health endpoint works
- [x] Create order endpoint works
- [x] Verify endpoint accepts requests
- [x] Error messages are user-friendly
- [x] Logging doesn't expose secrets
- [x] Frontend calls correct endpoints
- [x] Environment variables loaded correctly

