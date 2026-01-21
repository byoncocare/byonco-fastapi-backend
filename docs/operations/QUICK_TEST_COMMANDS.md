# Quick Test Commands - Backend Endpoints

Replace `https://your-backend.onrender.com` with your actual Render backend URL.

---

## 1. Health Check

```bash
curl https://your-backend.onrender.com/health
```

**Expected:** `{"status": "ok", "service": "byonco-api"}`

---

## 2. Environment Check

```bash
curl https://your-backend.onrender.com/api/debug/env-check
```

**Expected:** All booleans should be `true`

```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

---

## 3. AI Builder

```bash
curl -X POST https://your-backend.onrender.com/api/ai/builder \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I need treatment for breast cancer in Mumbai with budget 5 lakhs",
    "city": "Mumbai",
    "budget_max": 500000
  }'
```

**Expected:** JSON response with treatment plans

---

## 4. AI Second Opinion

```bash
curl -X POST https://your-backend.onrender.com/api/ai/second-opinion \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I have been diagnosed with stage 2 breast cancer. What treatment options do I have?",
    "profile": {
      "age": 45,
      "gender": "Female"
    }
  }'
```

**Expected:** JSON response with medical advice

---

## 5. Create Payment Order

```bash
curl -X POST https://your-backend.onrender.com/api/payments/create-order-byonco \
  -H "Content-Type: application/json" \
  -d '{
    "amount_inr": 49900,
    "purpose": "second_opinion",
    "user_id": "test-user-id-123",
    "metadata": {
      "request_id": "req-123"
    }
  }'
```

**Expected:**
```json
{
  "order_id": "order_xxx",
  "amount": 49900,
  "currency": "INR",
  "key_id": "rzp_test_..."
}
```

---

## 6. Verify Payment

**Note:** Requires actual Razorpay payment_id and signature from a completed payment.

```bash
curl -X POST https://your-backend.onrender.com/api/payments/verify-byonco \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "signature_xxx",
    "purpose": "second_opinion",
    "user_id": "test-user-id-123",
    "metadata": {
      "request_id": "req-123"
    }
  }'
```

**Expected:**
```json
{
  "verified": true,
  "message": "Payment verified and entitlements unlocked"
}
```

---

## PowerShell Commands (Windows)

If using PowerShell on Windows, escape JSON properly:

```powershell
# Health Check
curl.exe https://your-backend.onrender.com/health

# Environment Check
curl.exe https://your-backend.onrender.com/api/debug/env-check

# AI Builder
curl.exe -X POST https://your-backend.onrender.com/api/ai/builder `
  -H "Content-Type: application/json" `
  -d '{\"prompt\": \"test\", \"city\": \"Mumbai\"}'

# Create Payment Order
curl.exe -X POST https://your-backend.onrender.com/api/payments/create-order-byonco `
  -H "Content-Type: application/json" `
  -d '{\"amount_inr\": 49900, \"purpose\": \"second_opinion\", \"user_id\": \"test-123\"}'
```

---

## Testing Checklist

- [ ] Health check returns 200
- [ ] Env-check shows all services configured
- [ ] AI Builder returns treatment plans
- [ ] AI Second Opinion returns medical advice
- [ ] Create Order returns order_id and key_id
- [ ] Verify Payment returns verified: true (after real payment)
- [ ] Check Supabase for payment record (after verification)
- [ ] Check Supabase for entitlements (subscription/appointment)

---

**See:** `GO_LIVE_CHECKLIST.md` for comprehensive testing guide.

