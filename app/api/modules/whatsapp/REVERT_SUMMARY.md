# WhatsApp Hardening Revert Summary

## Step 1: Revert Complete ✅

### Commits Reverted
- **Hardening Commit:** `f3a5b91` - "Production-harden WhatsApp integration: signature verification, MongoDB persistence, retry/backoff, compliance, full ByOnco intake flow"
- **Revert Commit:** `3513e7a` - "Revert production hardening: restore working WhatsApp webhook behavior"

### Files Restored to Working State

1. **`backend/whatsapp/api_routes.py`**
   - ✅ Removed signature verification
   - ✅ Removed MongoDB store dependency
   - ✅ Restored in-memory store usage
   - ✅ Restored simple synchronous `get_response_for_user()` call
   - ✅ No signature check in POST webhook

2. **`backend/whatsapp/messages.py`**
   - ✅ Restored synchronous function (not async)
   - ✅ Restored simple onboarding flow (name, age, city)
   - ✅ Removed 6-essentials intake flow
   - ✅ Removed STOP/START/HELP compliance

3. **`backend/whatsapp/client.py`**
   - ✅ Removed retry/backoff wrapper
   - ✅ Restored simple `send_text_message()` function
   - ✅ No exponential backoff

4. **`backend/whatsapp/config.py`**
   - ✅ Removed `META_APP_SECRET`, `DEBUG_KEY`, `WHATSAPP_WABA_ID`
   - ✅ Restored original config structure

5. **`backend/server.py`**
   - ✅ Restored `create_whatsapp_router()` (no db parameter)
   - ✅ Health endpoint still present (was added before hardening)

6. **Files Deleted:**
   - `backend/whatsapp/signature.py` - Removed
   - `backend/whatsapp/store_mongo.py` - Removed
   - `backend/whatsapp/PRODUCTION_HARDENING_SUMMARY.md` - Removed
   - `backend/whatsapp/PRODUCTION_TESTING.md` - Removed

### Current Working State

- ✅ POST webhook uses in-memory store
- ✅ No signature verification (webhook accepts all requests)
- ✅ Simple onboarding: consent → name → age → city → menu
- ✅ No retry/backoff (direct Graph API calls)
- ✅ Webhook path unchanged: `/api/whatsapp/webhook`
- ✅ GET verification unchanged (still works)

## Step 2: Production Verification Required

**WAIT FOR CONFIRMATION** before proceeding to Step 3.

### Verification Checklist

After Render deploys commit `3513e7a`:

1. **Send test message from real phone:**
   - Send "Hi" to business number
   - Expected: Receive disclaimer message

2. **Check Render logs for:**
   - ✅ `POST /api/whatsapp/webhook - 200`
   - ✅ `Parsed 1 incoming message(s)`
   - ✅ `Sent WhatsApp message to ...`
   - ✅ `✅ Sent reply to ...`

3. **Confirm phone receives reply:**
   - Should receive: "Hi — I'm ByOnco's Cancer Support Assistant..."

**ONLY PROCEED TO STEP 3 AFTER CONFIRMING STEP 2 WORKS**

## Step 3: Re-apply Hardening with Feature Flags (Pending)

Once Step 2 is confirmed, we will re-apply hardening behind these flags:

- `WHATSAPP_ENFORCE_SIGNATURE=false` (default: false)
- `WHATSAPP_USE_MONGO_IDEMPOTENCY=false` (default: false)
- `WHATSAPP_USE_INTAKE_FLOW=false` (default: false)
- `WHATSAPP_ENABLE_RETRIES=true` (default: true, safe)

## Deployment Status

- ✅ Revert committed: `3513e7a`
- ✅ Pushed to main branch
- ✅ Synced to `byonco-fastapi-backend` repository
- ⏳ **WAITING FOR PRODUCTION VERIFICATION**

