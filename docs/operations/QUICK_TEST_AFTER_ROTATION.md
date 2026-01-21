# Quick Test Commands - After Key Rotation

Use these commands to verify new keys are active and working.

**Replace `https://your-backend.onrender.com` with your actual Render backend URL.**

---

## 1. Environment Check

```bash
curl https://your-backend.onrender.com/api/debug/env-check
```

**Expected Response:**
```json
{
  "openai_configured": true,
  "razorpay_configured": true,
  "supabase_configured": true
}
```

**If any is `false`:**
- Check variable name is correct (case-sensitive)
- Verify key was saved in Render
- Check service restarted after update
- Verify key format is correct

---

## 2. AI Builder Test

```bash
curl -X POST https://your-backend.onrender.com/api/ai/builder \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I need treatment for breast cancer in Mumbai",
    "city": "Mumbai",
    "budget_max": 500000
  }'
```

**Expected Response:**
```json
{
  "answer": "[JSON array of treatment plans]",
  "model": "gpt-4",
  "usage": {...}
}
```

**If Error:**
- Check `OPENAI_API_KEY` is set correctly
- Verify key is active in OpenAI dashboard
- Check OpenAI API quota/limits
- Review Render logs for detailed error

---

## 3. AI Second Opinion Test

```bash
curl -X POST https://your-backend.onrender.com/api/ai/second-opinion \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the treatment options for stage 2 breast cancer?",
    "profile": {
      "age": 45,
      "gender": "Female"
    }
  }'
```

**Expected Response:**
```json
{
  "answer": "Based on your diagnosis...",
  "safe": true,
  "paywall_required": false,
  "amount_inr": null,
  "error": null
}
```

**If Error:**
- Check `OPENAI_API_KEY` is set correctly
- Verify key is active in OpenAI dashboard
- Check OpenAI API quota/limits

---

## 4. Create Payment Order Test

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

**Expected Response:**
```json
{
  "order_id": "order_xxx",
  "amount": 49900,
  "currency": "INR",
  "key_id": "rzp_test_..."
}
```

**If Error:**
- Check `RAZORPAY_KEY_ID` is set correctly
- Check `RAZORPAY_KEY_SECRET` is set correctly
- Verify keys are active in Razorpay dashboard
- Check Razorpay account status

---

## 5. Payment Verification Test

**Note:** Requires actual Razorpay payment_id and signature from a completed payment.

```bash
curl -X POST https://your-backend.onrender.com/api/payments/verify-byonco \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "signature_xxx",
    "purpose": "second_opinion",
    "user_id": "test-user-id-123"
  }'
```

**Expected Response:**
```json
{
  "verified": true,
  "message": "Payment verified and entitlements unlocked"
}
```

**If Error:**
- Check `RAZORPAY_KEY_SECRET` is correct (signature verification)
- Check `SUPABASE_SERVICE_ROLE_KEY` is correct (database write)
- Verify Supabase connection
- Check Supabase payments table for new record

---

## 6. Verify Database Write

After payment verification, check Supabase:

```sql
-- Run in Supabase SQL Editor
SELECT * FROM payments 
WHERE order_id = 'order_xxx' 
ORDER BY created_at DESC 
LIMIT 1;
```

**Expected:**
- ✅ Record exists
- ✅ `status` = 'completed'
- ✅ `payment_id` = Razorpay payment ID
- ✅ `user_id` = User UUID

---

## PowerShell Commands (Windows)

```powershell
# Environment Check
curl.exe https://your-backend.onrender.com/api/debug/env-check

# AI Builder
curl.exe -X POST https://your-backend.onrender.com/api/ai/builder `
  -H "Content-Type: application/json" `
  -d '{\"prompt\": \"test\", \"city\": \"Mumbai\"}'

# Create Order
curl.exe -X POST https://your-backend.onrender.com/api/payments/create-order-byonco `
  -H "Content-Type: application/json" `
  -d '{\"amount_inr\": 49900, \"purpose\": \"second_opinion\", \"user_id\": \"test-123\"}'
```

---

## Success Criteria

After key rotation, all tests should pass:

- [ ] Env-check shows all services configured (`true`)
- [ ] AI Builder returns valid treatment plans
- [ ] AI Second Opinion returns valid medical advice
- [ ] Create Order returns order_id and key_id
- [ ] Payment verification writes to Supabase (check database)
- [ ] No errors in Render logs
- [ ] All endpoints respond within acceptable time

---

## Troubleshooting

### OpenAI Not Working
- Verify `OPENAI_API_KEY` format (starts with `sk-`)
- Check OpenAI dashboard for key status
- Verify API quota/limits
- Check Render logs for detailed error

### Razorpay Not Working
- Verify both `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set
- Check Razorpay dashboard for key status
- Verify account is active
- Check Render logs for detailed error

### Supabase Not Working
- Verify `SUPABASE_URL` format (`https://xxx.supabase.co`)
- Verify `SUPABASE_SERVICE_ROLE_KEY` is service_role key (not anon key)
- Check Supabase dashboard for project status
- Verify database connection
- Check Render logs for detailed error

---

**See:** `KEY_ROTATION_CHECKLIST.md` for complete rotation procedures.

