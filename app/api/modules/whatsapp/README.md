# WhatsApp Business Cloud API Integration

## Overview

Production-ready WhatsApp webhook integration for ByOnco Cancer Copilot. Handles Meta webhook verification, incoming messages, outbound messaging, and conversation state management.

## Architecture

### Modules

- **`config.py`** - Environment variable management and validation
- **`store.py`** - In-memory state store (easily replaceable with database)
- **`parser.py`** - Webhook payload parsing and message extraction
- **`client.py`** - WhatsApp Business Cloud API client for sending messages
- **`messages.py`** - Conversation flow logic and message templates
- **`api_routes.py`** - FastAPI routes for webhooks and admin endpoints

## Environment Variables

Required environment variables (set in Render dashboard):

```bash
WHATSAPP_VERIFY_TOKEN=praesidio_whatsapp_verify  # Must match Meta webhook config
WHATSAPP_ACCESS_TOKEN=<your_permanent_token>      # Meta System User token
WHATSAPP_PHONE_NUMBER_ID=<your_phone_number_id>  # Meta phone number ID
WHATSAPP_GRAPH_VERSION=v21.0                      # Optional, defaults to v21.0
APP_ENV=production                                 # production|staging|local
ADMIN_API_KEY=<optional_admin_key>                 # For /send endpoint protection
```

## API Endpoints

### 1. Webhook Verification (GET)
```
GET /api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=praesidio_whatsapp_verify&hub.challenge=123
```
Returns: Plain text challenge value (for Meta verification)

### 2. Webhook Handler (POST)
```
POST /api/whatsapp/webhook
```
Handles incoming WhatsApp messages from Meta. Processes messages and sends replies based on conversation state.

### 3. Send Message (POST)
```
POST /api/whatsapp/send
Headers: X-Admin-Key: <admin_key> (required in production)
Body: {
  "to": "919876543210",
  "text": "Your message here"
}
```

### 4. Self-Test (GET)
```
GET /api/whatsapp/debug/selftest
```
Returns configuration status (no sensitive data exposed).

## Conversation Flow

1. **First Contact** → Disclaimer message + "reply AGREE"
2. **After AGREE** → Onboarding sequence:
   - Name → Age → City
3. **Onboarding Complete** → Main menu with options:
   - Reports
   - Side effects & symptoms
   - Nutrition
   - Hospital & costs

## State Management

User state stored in-memory (can be swapped to database):
- `consented`: Boolean
- `onboarding_step`: "none" | "name" | "age" | "city" | "complete"
- `profile`: { name, age, city }

## Security

- ✅ No secrets in code (env vars only)
- ✅ Idempotency (duplicate message IDs ignored)
- ✅ Admin endpoint protection (X-Admin-Key header)
- ✅ Minimal PII storage
- ✅ No sensitive data in logs

## Testing

### Local Testing

1. Set environment variables in `.env` file
2. Start server: `uvicorn server:app --reload`
3. Test webhook verification:
   ```bash
   curl "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=praesidio_whatsapp_verify&hub.challenge=123"
   ```
4. Check self-test:
   ```bash
   curl http://localhost:8000/api/whatsapp/debug/selftest
   ```

### Production Testing

1. Configure webhook URL in Meta dashboard:
   `https://byonco-fastapi-backend.onrender.com/api/whatsapp/webhook`
2. Set verify token: `praesidio_whatsapp_verify`
3. Test webhook verification via Meta dashboard
4. Send test message from WhatsApp to your number

## Deployment

The WhatsApp router is automatically included in `server.py`. No additional configuration needed beyond environment variables.

## Future Enhancements

- Replace in-memory store with MongoDB/PostgreSQL
- Add interactive message templates (buttons, lists)
- Integrate with OpenAI/Azure for AI responses
- Add conversation history persistence
- Implement rate limiting

