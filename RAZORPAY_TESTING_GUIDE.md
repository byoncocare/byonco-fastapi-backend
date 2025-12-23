# Razorpay End-to-End Testing Guide

## 1. Verify Endpoints in /docs

Start the server:
```bash
python -m uvicorn server:app --reload
```

Visit: `http://localhost:8000/docs`

You should see under **"Razorpay"** tag:
- `GET /api/payments/razorpay/health` - Health check
- `POST /api/payments/razorpay/create-order` - Create order
- `POST /api/payments/razorpay/verify` - Verify payment

## 2. Environment Variables

Ensure `.env` file exists in backend root with:
```bash
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=your_test_secret
```

**Note**: `load_dotenv()` is already configured in `server.py` (line 20) to load from backend root `.env` file.

## 3. Health Check Endpoint

### Test Health Check
```bash
curl http://localhost:8000/api/payments/razorpay/health
```

**Expected Response** (200 OK):
```json
{
  "status": "ok",
  "razorpay_configured": true,
  "key_id_present": true
}
```

**If not configured**:
```json
{
  "status": "ok",
  "razorpay_configured": false,
  "key_id_present": false
}
```

## 4. Create Order Endpoint

### Test Create Order (Non-prescription, No Coupon)
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "vayu-ai-glasses",
    "variantId": "non-prescription",
    "quantity": 1
  }'
```

**Expected Response** (200 OK):
```json
{
  "orderId": "VAYU-2025-ABC123",
  "amount": 59999.0,
  "currency": "INR",
  "keyId": "rzp_test_..."
}
```

### Test Create Order (Prescription, With Coupon)
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

**Expected Response** (200 OK):
```json
{
  "orderId": "VAYU-2025-XYZ789",
  "amount": 58499.1,
  "currency": "INR",
  "keyId": "rzp_test_..."
}
```

**Note**: Amount is in INR (not paise). The `keyId` is the public Razorpay key ID (safe to expose).

### Error Cases

**Invalid Product**:
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "invalid-product",
    "variantId": "non-prescription",
    "quantity": 1
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Unknown product: invalid-product"
}
```

**Invalid Coupon**:
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "vayu-ai-glasses",
    "variantId": "non-prescription",
    "quantity": 1,
    "couponCode": "INVALID"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Invalid coupon code"
}
```

## 5. Verify Payment Endpoint

### Test Verify Payment
```bash
curl -X POST http://localhost:8000/api/payments/razorpay/verify \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_order_id": "order_ABC123XYZ",
    "razorpay_payment_id": "pay_DEF456UVW",
    "razorpay_signature": "abc123def456..."
  }'
```

**Expected Response** (Success - 200 OK):
```json
{
  "ok": true
}
```

**Expected Response** (Invalid Signature - 200 OK):
```json
{
  "ok": false,
  "error": "Invalid payment signature"
}
```

**Note**: This endpoint returns `200 OK` even for invalid signatures (security best practice). Check the `ok` field.

## 6. Frontend Configuration

The frontend (`VayuCheckoutPage.jsx`) is configured to use:
- **Backend URL**: `process.env.REACT_APP_BACKEND_URL || "https://byonco-fastapi-backend.onrender.com"`
- **Create Order**: `${BACKEND_URL}/api/payments/razorpay/create-order`
- **Verify Payment**: `${BACKEND_URL}/api/payments/razorpay/verify`

### For Local Development

Set in frontend `.env` or `.env.local`:
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

### For Production

Set:
```bash
REACT_APP_BACKEND_URL=https://byonco-fastapi-backend.onrender.com
```

## 7. Error Messages

All endpoints return JSON with consistent error format:

**Validation Errors** (400):
```json
{
  "detail": "User-friendly error message"
}
```

**Server Errors** (500):
```json
{
  "detail": "User-friendly error message (no internal details)"
}
```

**Payment Verification** (200):
```json
{
  "ok": false,
  "error": "User-friendly error message"
}
```

## 8. Logging

Logs are written to console (no secrets exposed):
- Order creation: Product, variant, quantity, coupon, order ID, amounts
- Payment verification: Order ID, payment ID (truncated), success/failure
- Errors: Error type and message (no secrets)

Example log output:
```
2025-12-23 11:30:00 - payments.razorpay - INFO - Creating Razorpay order: product=vayu-ai-glasses, variant=non-prescription, quantity=1, coupon=none
2025-12-23 11:30:00 - payments.razorpay - INFO - Order VAYU-2025-ABC123: calculated total=59999.0 INR (5999900 paise)
2025-12-23 11:30:01 - payments.razorpay - INFO - Order VAYU-2025-ABC123: Razorpay order created successfully, razorpay_order_id=order_xyz789
```

## 9. Security Checklist

✅ `RAZORPAY_KEY_SECRET` never exposed to frontend
✅ `RAZORPAY_KEY_SECRET` never logged
✅ Only public `keyId` returned to clients
✅ All pricing calculated server-side
✅ Payment signatures verified server-side
✅ Error messages are user-friendly (no internal details)
✅ All responses are JSON

## 10. End-to-End Test Flow

1. **Frontend**: User fills checkout form
2. **Frontend**: Calls `POST /api/payments/razorpay/create-order`
3. **Backend**: Returns `orderId`, `amount`, `currency`, `keyId`
4. **Frontend**: Opens Razorpay checkout with returned data
5. **User**: Completes payment in Razorpay
6. **Razorpay**: Returns `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`
7. **Frontend**: Calls `POST /api/payments/razorpay/verify` with payment data
8. **Backend**: Verifies signature, returns `{"ok": true}`
9. **Frontend**: Shows success page

## 11. Troubleshooting

### Issue: "razorpay package not installed"
**Solution**: `pip install razorpay setuptools`

### Issue: "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set"
**Solution**: Ensure `.env` file exists in backend root with both variables

### Issue: CORS errors from frontend
**Solution**: Check CORS middleware in `server.py` allows frontend origin

### Issue: Health check returns `razorpay_configured: false`
**Solution**: Verify `.env` file is in backend root and variables are set correctly

