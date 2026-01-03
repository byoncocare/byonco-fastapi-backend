# WhatsApp Production Testing Guide

## Prerequisites

### Environment Variables (Render Dashboard)

Ensure these are set:
- `WHATSAPP_ACCESS_TOKEN` - Permanent System User token
- `WHATSAPP_PHONE_NUMBER_ID` - Your phone number ID (e.g., 958423034009998)
- `WHATSAPP_VERIFY_TOKEN` - Must match Meta dashboard (e.g., praesidio_whatsapp_verify)
- `WHATSAPP_GRAPH_VERSION` - Graph API version (default: v21.0)
- `META_APP_SECRET` - App secret for signature verification (REQUIRED for production)
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `DEBUG_KEY` - Optional, for debug endpoints
- `WHATSAPP_WABA_ID` - Optional, WhatsApp Business Account ID

## Local Testing

### 1. Start Local Server

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### 3. Test Webhook Verification (GET)

```bash
# Replace YOUR_VERIFY_TOKEN with your actual token
curl "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

Expected: `test123` (plain text, 200 OK)

### 4. Test Webhook POST (with signature)

**Note:** For local testing, signature verification may be disabled if `META_APP_SECRET` is not set.

```bash
# Sample webhook payload (no signature for local testing)
curl -X POST "http://localhost:8000/api/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "test",
      "changes": [{
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {"phone_number_id": "958423034009998"},
          "messages": [{
            "from": "919876543210",
            "id": "wamid.test123",
            "timestamp": "1234567890",
            "type": "text",
            "text": {"body": "Hi"}
          }]
        }
      }]
    }]
  }'
```

Expected: `{"status":"ok"}` (200 OK)

### 5. Test Debug Endpoints (Protected)

```bash
# Without debug key (should fail if DEBUG_KEY is set)
curl http://localhost:8000/api/whatsapp/debug/waba

# With debug key
curl -H "X-Debug-Key: YOUR_DEBUG_KEY" http://localhost:8000/api/whatsapp/debug/waba
```

## Production Testing (Render)

### 1. Health Check

```bash
curl https://byonco-fastapi-backend.onrender.com/health
```

Expected: `{"status":"ok"}`

### 2. Webhook Verification

```bash
# Replace YOUR_VERIFY_TOKEN
curl "https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

Expected: `test123` (200 OK)

### 3. Check Webhook Status

```bash
curl https://byonco-fastapi-backend.onrender.com/api/whatsapp/debug/webhook-status
```

Expected: JSON with boolean flags (no secrets)

## WhatsApp Conversation Testing

### Test Flow 1: New User - Full Intake

1. **Send:** `Hi`
   - **Expected:** Disclaimer message + "reply AGREE"

2. **Send:** `AGREE`
   - **Expected:** "What type of cancer are you or your loved one dealing with?"

3. **Send:** `Breast cancer`
   - **Expected:** "What stage is the cancer?"

4. **Send:** `Stage 2`
   - **Expected:** "Which city are you in, and how far are you willing to travel?"

5. **Send:** `Mumbai, up to 500 km`
   - **Expected:** "What's your budget or insurance scheme?"

6. **Send:** `5 lakhs`
   - **Expected:** "How urgent is this?"

7. **Send:** `Within 1 month`
   - **Expected:** "What do you need most right now? 1) Hospital 2) Doctor 3) Second opinion 4) Lab"

8. **Send:** `1`
   - **Expected:** Recommendations list + "Talk to coordinator" option

### Test Flow 2: STOP/START Compliance

1. **Send:** `STOP`
   - **Expected:** "You've opted out of messages. Reply START to receive messages again."

2. **Send:** `Hi` (should be ignored)
   - **Expected:** "You've opted out..." (or no response)

3. **Send:** `START`
   - **Expected:** "Welcome back! You're now receiving messages again."

4. **Send:** `Hi`
   - **Expected:** Normal disclaimer/response

### Test Flow 3: HELP Command

1. **Send:** `HELP`
   - **Expected:** Help message with options

### Test Flow 4: Returning User

1. **Send:** `Hi` (user who completed intake)
   - **Expected:** Menu with options 1-4

2. **Send:** `1`
   - **Expected:** Hospital recommendations

3. **Send:** `AGREE`
   - **Expected:** Restart intake flow

## MongoDB Verification

### Check Collections

After testing, verify data in MongoDB:

```javascript
// Connect to MongoDB
use your_database_name

// Check processed messages
db.processed_message_ids.find().limit(5)

// Check user states
db.whatsapp_user_state.find().limit(5)

// Check user preferences
db.whatsapp_user_prefs.find().limit(5)

// Check opt-outs
db.whatsapp_user_optout.find()
```

### Verify Indexes

```javascript
// Check indexes
db.processed_message_ids.getIndexes()
db.whatsapp_user_state.getIndexes()
db.whatsapp_user_optout.getIndexes()
```

Expected indexes:
- `message_id_unique` on `processed_message_ids`
- `wa_id_unique` on `whatsapp_user_state`
- `optout_wa_id_unique` on `whatsapp_user_optout`
- TTL index on `processed_at` (30 days)

## Render Logs Verification

### Check Logs for:

1. **Signature Verification:**
   - Look for: "Webhook signature verification failed" (should NOT appear for valid requests)

2. **Idempotency:**
   - Look for: "Message ... already processed, skipping"

3. **State Transitions:**
   - Look for: "User **** consented, starting intake"
   - Look for: "User **** completed intake, saved prefs"

4. **Retry Logic:**
   - Look for: "Retry 1/3" (only on 429/5xx errors)

5. **Masked Logging:**
   - Phone numbers should show as `****1234` (last 4 digits only)
   - No full tokens or secrets in logs

## Troubleshooting

### Signature Verification Fails

**Symptom:** Webhook returns 403, logs show "signature verification failed"

**Fix:**
- Verify `META_APP_SECRET` is set correctly in Render
- Ensure signature header format: `sha256=<hex>`
- Check that raw body is being read correctly (no double parsing)

### Messages Not Processed

**Symptom:** Messages received but no reply

**Check:**
- Render logs for errors
- MongoDB connection (check `MONGO_URL`)
- Verify message parsing (check logs for "Parsed X incoming message(s)")

### Duplicate Messages

**Symptom:** Same message processed multiple times

**Fix:**
- Check MongoDB `processed_message_ids` collection
- Verify unique index exists on `message_id`
- Check idempotency check is working (logs should show "already processed")

### Retry Not Working

**Symptom:** 429/5xx errors not retried

**Check:**
- Verify retry logic in `client.py`
- Check logs for retry attempts
- Ensure exponential backoff is working

## Success Criteria

✅ Health endpoint returns 200 OK
✅ Webhook verification returns challenge
✅ POST webhook returns 200 OK (even on errors)
✅ Signature verification works (403 on invalid)
✅ STOP/START/HELP commands work
✅ Full intake flow collects 6 essentials
✅ Recommendations generated after intake
✅ MongoDB stores all data correctly
✅ Idempotency prevents duplicates
✅ Retry works on 429/5xx
✅ Logs are clean (no secrets, masked phone numbers)
✅ Debug endpoints protected by DEBUG_KEY

## Next Steps

After validation:
1. Monitor Render logs for production traffic
2. Check MongoDB collections for data quality
3. Review recommendations quality (can enhance with AI later)
4. Set up alerts for webhook failures
5. Monitor Graph API rate limits

