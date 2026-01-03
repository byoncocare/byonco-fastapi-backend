# WhatsApp Production Hardening - Implementation Summary

## Overview

Production-hardened WhatsApp Cloud API integration with signature verification, MongoDB persistence, retry/backoff, compliance features, and full ByOnco intake flow.

## Files Created/Modified

### New Files
1. **`backend/whatsapp/signature.py`** - Meta webhook signature verification using HMAC SHA256
2. **`backend/whatsapp/store_mongo.py`** - MongoDB-backed store for user state, idempotency, and opt-outs
3. **`backend/whatsapp/PRODUCTION_TESTING.md`** - Comprehensive testing guide

### Modified Files
1. **`backend/whatsapp/config.py`** - Added `META_APP_SECRET`, `DEBUG_KEY`, `WHATSAPP_WABA_ID`
2. **`backend/whatsapp/client.py`** - Added retry/backoff wrapper for Graph API calls (429/5xx only)
3. **`backend/whatsapp/messages.py`** - Complete rewrite with:
   - STOP/START/HELP compliance
   - Full 6-essentials intake flow
   - Recommendations generation
4. **`backend/whatsapp/api_routes.py`** - Complete rewrite with:
   - Signature verification
   - MongoDB store integration
   - Enhanced logging hygiene
   - Debug endpoints with DEBUG_KEY protection
5. **`backend/server.py`** - Added `/health` endpoint, pass `db` to WhatsApp router

## Key Features Implemented

### 1. Security Hardening ✅
- **Signature Verification:** Verifies `X-Hub-Signature-256` header using `META_APP_SECRET`
- **Constant-time comparison:** Uses `hmac.compare_digest()` to prevent timing attacks
- **Raw body parsing:** Reads raw bytes before JSON parsing to ensure signature accuracy

### 2. Persistent Idempotency ✅
- **MongoDB storage:** `processed_message_ids` collection with unique index
- **TTL index:** Auto-deletes processed messages after 30 days
- **Duplicate prevention:** Checks MongoDB before processing

### 3. Reliability (Retry/Backoff) ✅
- **Exponential backoff:** 1s, 2s, 4s with jitter
- **Retries on:** 429 (rate limit), 500, 502, 503, 504
- **No retry on:** 400, 401, 403 (client errors)
- **Max retries:** 3 attempts

### 4. Compliance (STOP/START/HELP) ✅
- **STOP:** Opts user out, stores in MongoDB
- **START:** Opts user back in, removes from opt-out collection
- **HELP:** Returns help message
- **Opt-out enforcement:** Ignores messages from opted-out users

### 5. ByOnco Intake Flow ✅
**6 Essentials Collected:**
1. Cancer type
2. Stage (if known)
3. City + travel radius
4. Budget/insurance scheme
5. Urgency (timeframe)
6. Need (hospital/doctor/second opinion/labs)

**Output:**
- 3-5 recommendations (rules-based, placeholder for AI)
- "Talk to coordinator" option
- Saves to `whatsapp_user_prefs` collection

### 6. Logging Hygiene ✅
- **Masked phone numbers:** Shows only last 4 digits (`****1234`)
- **No secrets:** Never logs tokens, app secrets, or full payloads
- **Structured logs:** Includes message_id, state transitions, timing
- **Event types:** Clear log messages for each event

### 7. Debug Endpoints ✅
- **`/api/whatsapp/debug/webhook-status`** - Public, safe status check
- **`/api/whatsapp/debug/waba`** - Protected by DEBUG_KEY
- **`/api/whatsapp/debug/token`** - Protected by DEBUG_KEY (masked tokens)
- **`/api/whatsapp/debug/selftest`** - Public, configuration check

### 8. Health Endpoint ✅
- **`GET /health`** - Simple health check, returns `{"status":"ok"}`

## MongoDB Schema

### Collections Created

1. **`processed_message_ids`**
   - Fields: `message_id` (unique), `processed_at` (TTL)
   - Index: Unique on `message_id`, TTL on `processed_at` (30 days)

2. **`whatsapp_user_state`**
   - Fields: `wa_id` (unique), `consented`, `state`, `step`, `collected_fields`, `created_at`, `updated_at`
   - Index: Unique on `wa_id`

3. **`whatsapp_user_prefs`**
   - Fields: `wa_id`, `cancer_type`, `stage`, `location`, `budget`, `urgency`, `need`, `saved_at`
   - Stores final intake answers

4. **`whatsapp_user_optout`**
   - Fields: `wa_id` (unique), `opted_out`, `opted_out_at`
   - Index: Unique on `wa_id`

## Environment Variables Required

```bash
# Required
WHATSAPP_ACCESS_TOKEN=<permanent_token>
WHATSAPP_PHONE_NUMBER_ID=<phone_number_id>
WHATSAPP_VERIFY_TOKEN=<verify_token>
META_APP_SECRET=<app_secret>  # NEW - Required for signature verification
MONGO_URL=<mongodb_connection_string>
DB_NAME=<database_name>

# Optional
WHATSAPP_GRAPH_VERSION=v21.0
DEBUG_KEY=<debug_key>  # NEW - For debug endpoints
WHATSAPP_WABA_ID=<waba_id>  # NEW - Optional
APP_ENV=production
```

## Breaking Changes

⚠️ **Important:** The WhatsApp router now requires `db` parameter:
- Old: `create_whatsapp_router()`
- New: `create_whatsapp_router(db)`

This is already fixed in `server.py`.

## Testing Checklist

See `PRODUCTION_TESTING.md` for complete testing guide.

**Quick Test:**
1. ✅ Health endpoint: `curl /health`
2. ✅ Webhook verification: `curl /api/whatsapp/webhook?hub.mode=subscribe&...`
3. ✅ WhatsApp flow: Send "Hi" → "AGREE" → complete intake
4. ✅ STOP/START: Send "STOP" → "START"
5. ✅ MongoDB: Verify collections and indexes

## Deployment Notes

1. **Set `META_APP_SECRET`** in Render dashboard (REQUIRED)
2. **Verify MongoDB connection** (`MONGO_URL` must be correct)
3. **Indexes auto-create** on first webhook request
4. **Signature verification** is enabled if `META_APP_SECRET` is set
5. **Debug endpoints** require `DEBUG_KEY` header if `DEBUG_KEY` env var is set

## Performance Considerations

- **Webhook response time:** Always returns 200 quickly, processing happens asynchronously
- **MongoDB indexes:** Created on first request (lazy initialization)
- **Retry delays:** Exponential backoff prevents overwhelming Graph API
- **TTL index:** Auto-cleans old processed messages (30 days)

## Security Considerations

- ✅ Signature verification prevents unauthorized webhook calls
- ✅ No secrets in logs (tokens, app secrets masked)
- ✅ Phone numbers masked in logs (last 4 digits only)
- ✅ Debug endpoints protected by DEBUG_KEY
- ✅ Constant-time signature comparison (timing attack prevention)

## Future Enhancements

- Replace rules-based recommendations with AI/ML
- Add conversation history persistence
- Implement rate limiting per user
- Add analytics and monitoring
- Enhance recommendations with hospital/doctor matching

