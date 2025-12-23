# Razorpay Import Fix Summary

## Problem
Runtime error: `'NoneType' object has no attribute 'Client'` when including payments_router.

## Root Cause
The existing `payments/service.py` was using:
```python
try:
    import razorpay
except ImportError:
    razorpay = None

if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(...)  # Fails if razorpay is None
```

This could fail if:
1. The `razorpay` package import failed and set `razorpay = None`
2. There was a naming collision with a file/folder named `razorpay`
3. The module-level initialization happened before env vars were loaded

## Solution Applied

### 1. Fixed `payments/service.py`
- Changed `import razorpay` → `import razorpay as razorpay_sdk`
- Created `_get_razorpay_client()` helper function for lazy initialization
- Added `_ensure_client()` method in `PaymentService` class
- Client is now created on-demand, not at module level
- Better error handling with clear messages

### 2. Created `payments/razorpay.py` (NEW)
- Vayu-specific Razorpay endpoints
- Uses `import razorpay as razorpay_sdk` with alias
- Helper functions: `_get_razorpay_client()`, `_get_key_id()`, `_get_key_secret()`
- Server-side pricing calculation for Vayu products
- Endpoints:
  - `POST /api/payments/razorpay/create-order`
  - `POST /api/payments/razorpay/verify`

### 3. Updated `server.py`
- Added import and router registration for Vayu Razorpay:
```python
from payments import razorpay as vayu_razorpay_router
app.include_router(vayu_razorpay_router.router)
```

## Files Modified

1. **`payments/service.py`** - Fixed imports and client initialization
2. **`payments/razorpay.py`** - NEW FILE - Vayu-specific endpoints
3. **`server.py`** - Added Vayu Razorpay router registration

## Testing

After these fixes, the server should start without errors:

```bash
python -m uvicorn server:app --reload
```

Expected output:
```
✅ Included payments_router
✅ Included vayu_razorpay_router
```

## Verification

1. **Check server starts**: No more `'NoneType' object has no attribute 'Client'` error
2. **Check /docs**: Should show both payment routers:
   - `/api/payments/*` (existing general payments)
   - `/api/payments/razorpay/*` (new Vayu endpoints)
3. **Test Vayu endpoints**:
   ```bash
   curl -X POST http://localhost:8000/api/payments/razorpay/create-order \
     -H "Content-Type: application/json" \
     -d '{"productId": "vayu-ai-glasses", "variantId": "non-prescription", "quantity": 1}'
   ```

## Security Notes

✅ No secrets are printed or logged
✅ Environment variables validated before use
✅ Client created only when needed
✅ Clear error messages without exposing internals
✅ Uses `razorpay_sdk` alias to avoid naming collisions

