# Key Rotation Checklist

**IMPORTANT:** Rotate keys immediately if they are exposed or compromised.

---

## OpenAI API Key Rotation

### Steps

1. **Generate New Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy the new key immediately (shown only once)
   - **DO NOT** close the page until you've saved it

2. **Update in Render:**
   - Go to Render Dashboard → Your Service → Environment
   - Find `OPENAI_API_KEY`
   - Click "Edit"
   - Replace with new key
   - Click "Save Changes"
   - Service will automatically restart

3. **Test New Key:**
   ```bash
   # Test env-check
   curl https://your-backend.onrender.com/api/debug/env-check
   # Should show: "openai_configured": true
   
   # Test AI endpoint
   curl -X POST https://your-backend.onrender.com/api/ai/builder \
     -H "Content-Type: application/json" \
     -d '{"prompt": "test", "city": "Mumbai"}'
   # Should return AI response (not error)
   ```

4. **Verify New Key Works:**
   - ✅ Env-check shows `openai_configured: true`
   - ✅ AI Builder endpoint returns valid response
   - ✅ AI Second Opinion endpoint returns valid response
   - ✅ No errors in Render logs

5. **Revoke Old Key:**
   - Go back to OpenAI Platform → API Keys
   - Find the old key
   - Click "Revoke" or "Delete"
   - Confirm deletion

6. **Monitor:**
   - Watch Render logs for 24 hours
   - Check for any API errors
   - Verify all AI endpoints still work

---

## Razorpay Secret Key Rotation

### Steps

1. **Generate New Keys:**
   - Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
   - Settings → API Keys
   - Click "Generate New Key"
   - Copy both **Key ID** and **Key Secret** immediately
   - **DO NOT** close the page until you've saved both

2. **Update in Render:**
   - Go to Render Dashboard → Your Service → Environment
   - Update `RAZORPAY_KEY_ID` with new Key ID
   - Update `RAZORPAY_KEY_SECRET` with new Key Secret
   - Click "Save Changes" for each
   - Service will automatically restart

3. **Test New Keys:**
   ```bash
   # Test env-check
   curl https://your-backend.onrender.com/api/debug/env-check
   # Should show: "razorpay_configured": true
   
   # Test create order
   curl -X POST https://your-backend.onrender.com/api/payments/create-order-byonco \
     -H "Content-Type: application/json" \
     -d '{"amount_inr": 49900, "purpose": "second_opinion", "user_id": "test-123"}'
   # Should return order_id and key_id
   ```

4. **Verify New Keys Work:**
   - ✅ Env-check shows `razorpay_configured: true`
   - ✅ Create Order endpoint returns order_id
   - ✅ Payment verification works (test with real payment)
   - ✅ No errors in Render logs

5. **Revoke Old Keys:**
   - Go back to Razorpay Dashboard → API Keys
   - Find the old key pair
   - Click "Revoke" or "Delete"
   - Confirm deletion

6. **Update Flutter App (if needed):**
   - If Flutter app uses `RAZORPAY_KEY_ID` in env.json, update it
   - Rebuild and redeploy Flutter app
   - Test payment flow end-to-end

7. **Monitor:**
   - Watch Render logs for 24 hours
   - Check payment success rate
   - Verify all payment endpoints still work

---

## Supabase Service Role Key Rotation

### Steps

1. **Generate New Key:**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project
   - Settings → API
   - Scroll to "service_role" key section
   - Click "Reset service_role key" or "Generate new key"
   - Copy the new key immediately
   - **Warning:** Old key becomes invalid immediately

2. **Update in Render:**
   - Go to Render Dashboard → Your Service → Environment
   - Find `SUPABASE_SERVICE_ROLE_KEY`
   - Click "Edit"
   - Replace with new key
   - Click "Save Changes"
   - Service will automatically restart

3. **Test New Key:**
   ```bash
   # Test env-check
   curl https://your-backend.onrender.com/api/debug/env-check
   # Should show: "supabase_configured": true
   
   # Test payment verification (this writes to Supabase)
   curl -X POST https://your-backend.onrender.com/api/payments/verify-byonco \
     -H "Content-Type: application/json" \
     -d '{
       "razorpay_order_id": "order_xxx",
       "razorpay_payment_id": "pay_xxx",
       "razorpay_signature": "sig_xxx",
       "purpose": "second_opinion",
       "user_id": "test-123"
     }'
   # Should return verified: true
   ```

4. **Verify New Key Works:**
   - ✅ Env-check shows `supabase_configured: true`
   - ✅ Payment verification writes to Supabase successfully
   - ✅ Check Supabase payments table for new records
   - ✅ Entitlements are unlocked correctly
   - ✅ No errors in Render logs

5. **Verify Database Access:**
   - Check Supabase logs for connection errors
   - Verify payment records are being written
   - Test subscription/appointment creation

6. **Monitor:**
   - Watch Render logs for 24 hours
   - Check Supabase logs for errors
   - Verify all database operations work

**Note:** Old service_role key is automatically invalidated when you generate a new one.

---

## Emergency Key Rotation (All Keys)

If keys are compromised:

1. **Immediate Actions:**
   - Generate new keys for ALL services (OpenAI, Razorpay, Supabase)
   - Update ALL keys in Render simultaneously
   - Restart service

2. **Verify All Services:**
   ```bash
   curl https://your-backend.onrender.com/api/debug/env-check
   # All should be true
   ```

3. **Test All Endpoints:**
   - AI Builder
   - AI Second Opinion
   - Create Payment Order
   - Verify Payment

4. **Revoke Old Keys:**
   - Revoke all old keys from provider dashboards
   - Monitor for unauthorized access attempts

5. **Security Audit:**
   - Check git history for exposed keys
   - Review access logs
   - Check for unauthorized API usage

---

## Pre-Rotation Checklist

Before rotating keys:

- [ ] Backup current key values (in secure password manager)
- [ ] Notify team about rotation (if applicable)
- [ ] Schedule during low-traffic period (if possible)
- [ ] Prepare test commands
- [ ] Have rollback plan ready

---

## Post-Rotation Checklist

After rotating keys:

- [ ] All env-check booleans are `true`
- [ ] All endpoints tested and working
- [ ] Old keys revoked from providers
- [ ] No errors in logs
- [ ] Flutter app updated (if needed)
- [ ] Team notified of completion
- [ ] Documentation updated (if needed)

---

## Rollback Plan

If new keys don't work:

1. **Restore Old Keys:**
   - Go to Render Dashboard
   - Restore previous key values
   - Restart service

2. **Verify Old Keys Work:**
   - Test env-check
   - Test one endpoint

3. **Investigate Issue:**
   - Check key format
   - Verify key permissions
   - Check provider dashboard for key status

4. **Retry Rotation:**
   - Generate new keys again
   - Follow rotation steps carefully

---

## Key Rotation Schedule

**Recommended:**
- **OpenAI:** Every 90 days (or if compromised)
- **Razorpay:** Every 180 days (or if compromised)
- **Supabase:** Every 180 days (or if compromised)

**Immediate Rotation Required:**
- Key exposed in git commit
- Key shared in chat/email
- Suspicious API usage detected
- Security breach suspected

---

## Testing After Rotation

Use these commands to verify new keys work:

```bash
# 1. Environment check
curl https://your-backend.onrender.com/api/debug/env-check

# 2. AI Builder test
curl -X POST https://your-backend.onrender.com/api/ai/builder \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "city": "Mumbai"}'

# 3. Create payment order test
curl -X POST https://your-backend.onrender.com/api/payments/create-order-byonco \
  -H "Content-Type: application/json" \
  -d '{"amount_inr": 49900, "purpose": "second_opinion", "user_id": "test-123"}'
```

**Expected Results:**
- ✅ Env-check: All booleans `true`
- ✅ AI Builder: Returns treatment plans
- ✅ Create Order: Returns order_id and key_id

---

**Status:** ✅ **READY FOR KEY ROTATION**

Follow this checklist whenever rotating keys.

