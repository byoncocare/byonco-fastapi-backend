# WhatsApp OpenAI Integration - Doctor-Like Responses

## Overview

This integration brings the same AI-powered cancer support functionality from the ByOnco website's "Second Opinion" feature to WhatsApp, providing doctor-like responses similar to August AI.

## Features

### 1. Enhanced Onboarding Flow
- **Name** → **Age** → **City** → **Country** → **Language** → **Complete**
- Supports 15 languages: English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Spanish, German, Russian, French, Portuguese, Japanese, Chinese

### 2. OpenAI Integration
- Uses the same `SecondOpinionAIService` as the website
- Cancer-only gating via system prompt
- Medical-safe responses with disclaimers
- Refusal/redirect for non-cancer topics
- No diagnosis / no "do this instead of doctor"

### 3. Menu-Driven Flow
After onboarding, users can:
1. **Reports** — Understand medical reports and test results
2. **Side effects & symptoms** — Get information about treatment side effects
3. **Nutrition** — Cancer-friendly diet and nutrition guidance
4. **Hospital & costs** — Find hospitals and estimate treatment costs

### 4. AI-Powered Responses
- When user selects a menu option or asks a direct question, OpenAI generates a contextual response
- Responses include user context (name, age, city, country)
- Responses respect user's language preference (currently responds in English; translation can be added)

## Implementation Details

### Files Modified

1. **`backend/whatsapp/store.py`**
   - Added `country` and `language` fields to user profile
   - Updated onboarding steps: `name` → `age` → `city` → `country` → `language` → `complete`

2. **`backend/whatsapp/messages.py`**
   - Added `get_response_for_user_async()` function that integrates OpenAI
   - Added `get_ai_response()` helper that calls `SecondOpinionAIService`
   - Added language normalization
   - Updated message templates to include country and language prompts

3. **`backend/whatsapp/api_routes.py`**
   - Updated to use `get_response_for_user_async()` instead of synchronous version
   - Webhook handler now awaits AI responses

### OpenAI System Prompt

The system uses the same cancer-focused prompt as the website:
- Only answers oncology-related questions
- Refuses non-medical and non-cancer questions
- Emphasizes AI assistance, not replacement for doctors
- Guides users to premium service for detailed second opinions

### Language Support

Currently, OpenAI responses are in English. To add full multi-language support:

1. **Option 1:** Add language instruction to system prompt
   ```python
   system_prompt += f"\n\nIMPORTANT: Respond in {user_language} language."
   ```

2. **Option 2:** Use translation API (Google Translate, DeepL) after OpenAI response

3. **Option 3:** Use OpenAI's native multilingual capabilities (GPT-4o supports many languages)

## Usage Flow

1. User sends "Hi" → Receives disclaimer
2. User replies "AGREE" → Onboarding starts
3. User provides: Name → Age → City → Country → Language
4. User sees menu: 1) Reports, 2) Side effects, 3) Nutrition, 4) Hospital & costs
5. User selects option or asks question → OpenAI generates response
6. Conversation continues with AI-powered responses

## Environment Variables Required

- `OPENAI_API_KEY` - Required for AI responses
- `WHATSAPP_ACCESS_TOKEN` - Required for sending messages
- `WHATSAPP_PHONE_NUMBER_ID` - Required for sending messages
- `WHATSAPP_VERIFY_TOKEN` - Required for webhook verification

## Testing

1. Send "Hi" to WhatsApp business number
2. Reply "AGREE"
3. Complete onboarding (name, age, city, country, language)
4. Select menu option (1-4) or ask a direct question
5. Verify OpenAI response is received

## Future Enhancements

- [ ] Full multi-language translation for responses
- [ ] File upload support (medical reports via WhatsApp)
- [ ] Conversation history persistence
- [ ] Integration with hospital/doctor database
- [ ] Cost calculator integration
- [ ] Appointment booking via WhatsApp

## Notes

- All responses are cancer/oncology-focused
- Non-cancer questions are politely redirected
- AI emphasizes consulting real doctors
- Premium second opinion service is promoted for detailed cases

