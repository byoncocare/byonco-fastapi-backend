# WhatsApp Webhook Testing Guide

## Quick Status Check

```bash
# Check webhook configuration (safe, no secrets exposed)
curl https://byonco-fastapi-backend.onrender.com/api/whatsapp/debug/webhook-status
```

Expected response:
```json
{
  "whatsapp_access_token_present": true,
  "whatsapp_verify_token_present": true,
  "whatsapp_phone_number_id_present": true,
  "webhook_ready": true
}
```

## 1. Test GET Webhook Verification (Local)

```bash
# Replace YOUR_VERIFY_TOKEN with your actual WHATSAPP_VERIFY_TOKEN
curl -X GET "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

**Expected Response:**
- Status: `200 OK`
- Body: `test123` (plain text)

**If verification fails:**
- Status: `403 Forbidden`
- Body: `Forbidden`

## 2. Test GET Webhook Verification (Production)

```bash
# Replace YOUR_VERIFY_TOKEN with your actual WHATSAPP_VERIFY_TOKEN
curl -X GET "https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

**Expected Response:**
- Status: `200 OK`
- Body: `test123` (plain text)

## 3. Test POST Webhook Handler (Local)

```bash
curl -X POST "http://localhost:8000/api/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [
      {
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [
          {
            "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                "display_phone_number": "1234567890",
                "phone_number_id": "958423034009998"
              },
              "contacts": [
                {
                  "profile": {
                    "name": "Test User"
                  },
                  "wa_id": "919876543210"
                }
              ],
              "messages": [
                {
                  "from": "919876543210",
                  "id": "wamid.test123",
                  "timestamp": "1234567890",
                  "type": "text",
                  "text": {
                    "body": "Hello"
                  }
                }
              ]
            },
            "field": "messages"
          }
        ]
      }
    ]
  }'
```

**Expected Response:**
- Status: `200 OK`
- Body: `{"status":"ok"}`

**Check logs for:**
- `POST /api/whatsapp/webhook - method=POST, path=/api/whatsapp/webhook`
- `Received webhook payload: object=whatsapp_business_account`
- `Parsed 1 incoming message(s)`
- `Incoming message: type=text, from=919876****210, message_id=wamid.test123`
- `✅ Sent reply to 919876****210`

## 4. Test POST Webhook Handler (Production)

```bash
curl -X POST "https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [
      {
        "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
        "changes": [
          {
            "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                "display_phone_number": "1234567890",
                "phone_number_id": "958423034009998"
              },
              "contacts": [
                {
                  "profile": {
                    "name": "Test User"
                  },
                  "wa_id": "919876543210"
                }
              ],
              "messages": [
                {
                  "from": "919876543210",
                  "id": "wamid.test123",
                  "timestamp": "1234567890",
                  "type": "text",
                  "text": {
                    "body": "Hello"
                  }
                }
              ]
            },
            "field": "messages"
          }
        ]
      }
    ]
  }'
```

**Expected Response:**
- Status: `200 OK`
- Body: `{"status":"ok"}`

**Check Render logs for:**
- Request logging: `📥 POST /api/whatsapp/webhook from <IP>`
- Webhook processing logs
- Response logging: `📤 POST /api/whatsapp/webhook - 200`

## 5. Test with Real WhatsApp Message

1. Send a WhatsApp message from your personal number to your business number
2. Check Render logs immediately
3. You should see:
   - Webhook POST request logged
   - Message parsed and processed
   - Reply sent (if configured)

## Meta Dashboard Configuration Checklist

### Step 1: Webhook Configuration

1. **Go to Meta Business Suite:**
   - Navigate to: https://business.facebook.com
   - Select your WhatsApp Business Account

2. **Access Webhook Settings:**
   - Go to: **WhatsApp** → **API Setup** → **Configuration**
   - Or: **WhatsApp Manager** → **API Setup** → **Webhooks**

3. **Configure Webhook:**
   - **Callback URL:** `https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook`
   - **Verify Token:** `praesidio_whatsapp_verify` (or your `WHATSAPP_VERIFY_TOKEN`)
   - Click **Verify and Save**

4. **Subscribe to Webhook Fields:**
   - ✅ **messages** (required for receiving messages)
   - ✅ **message_status** (optional, for delivery receipts)
   - ✅ **message_template_status_update** (optional, for template status)

### Step 2: WABA Webhook Subscription

1. **Go to App Dashboard:**
   - Navigate to: https://developers.facebook.com
   - Select your app

2. **Webhooks Section:**
   - Go to: **Webhooks** → **WhatsApp Business Account**
   - Ensure webhook is **subscribed** and shows green status

3. **Verify Webhook Status:**
   - Status should show: **Subscribed** ✅
   - Last delivery should show recent timestamp

### Step 3: Phone Number Verification

1. **Check Phone Number Status:**
   - Go to: **WhatsApp Manager** → **Phone Numbers**
   - Your number should show: **Connected** ✅

2. **Verify Registration:**
   - If not connected, run the registration script:
     ```bash
     python scripts/register_whatsapp_number.py
     ```

### Step 4: Test Webhook

1. **Use Meta's Test Tool:**
   - In Webhook settings, click **Test** button
   - Meta will send a test webhook

2. **Check Render Logs:**
   - Should see webhook POST request
   - Should see successful processing

3. **Send Real Message:**
   - Send WhatsApp message from personal number
   - Check logs for incoming message and reply

## Troubleshooting

### Webhook Verification Fails (403)

**Possible causes:**
- Verify token mismatch
- Wrong webhook URL
- CORS blocking (shouldn't happen, but check)

**Fix:**
- Verify `WHATSAPP_VERIFY_TOKEN` in Render matches Meta dashboard
- Check webhook URL is exactly: `https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook`
- Test with curl command above

### No Messages Received

**Possible causes:**
- Webhook not subscribed
- Phone number not registered
- Wrong phone_number_id

**Fix:**
- Check Meta dashboard: Webhook status should be "Subscribed"
- Verify phone number shows "Connected" in WhatsApp Manager
- Verify `WHATSAPP_PHONE_NUMBER_ID` matches your phone number ID

### Messages Received But No Reply

**Possible causes:**
- Access token expired/invalid
- Missing permissions
- API error

**Fix:**
- Check Render logs for error messages
- Verify `WHATSAPP_ACCESS_TOKEN` is valid and has `whatsapp_business_messaging` permission
- Test with debug endpoint: `/api/whatsapp/debug/selftest`

### Logs Not Showing

**Possible causes:**
- Request logging middleware not working
- Log level too high

**Fix:**
- Check Render logs are enabled
- Verify middleware is added in `server.py`
- Check log level is `INFO` or lower

## Environment Variables Checklist

Ensure these are set in Render dashboard:

- ✅ `WHATSAPP_VERIFY_TOKEN` - Must match Meta dashboard
- ✅ `WHATSAPP_ACCESS_TOKEN` - Permanent System User token
- ✅ `WHATSAPP_PHONE_NUMBER_ID` - Your phone number ID (e.g., 958423034009998)
- ✅ `WHATSAPP_GRAPH_VERSION` - Graph API version (default: v21.0)
- ✅ `APP_ENV` - Environment (production/staging/local)

## Success Indicators

✅ Webhook verification returns 200 with challenge
✅ POST webhook returns 200 OK immediately
✅ Logs show incoming messages parsed
✅ Logs show replies sent
✅ Real WhatsApp messages trigger webhook
✅ Replies are received on WhatsApp

