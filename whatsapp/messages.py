"""
Message templates and conversation flow logic for ByOnco Cancer Support Assistant
Integrated with OpenAI for information and guidance (helps prepare questions for oncologist)
All messages are original ByOnco branding
"""
from typing import Dict, Optional, Tuple
from .store import store
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

# Inactivity timeout: 10 minutes
INACTIVITY_TIMEOUT_MINUTES = 10

# Supported languages mapping
LANGUAGE_CODES = {
    "english": "en", "en": "en",
    "hindi": "hi", "hi": "hi",
    "marathi": "mr", "mr": "mr",
    "tamil": "ta", "ta": "ta",
    "telugu": "te", "te": "te",
    "bengali": "bn", "bn": "bn",
    "gujarati": "gu", "gu": "gu",
    "kannada": "kn", "kn": "kn",
    "spanish": "es", "es": "es",
    "german": "de", "de": "de",
    "russian": "ru", "ru": "ru",
    "french": "fr", "fr": "fr",
    "portuguese": "pt", "pt": "pt",
    "japanese": "ja", "ja": "ja",
    "chinese": "zh", "zh": "zh"
}

# Message templates (English base - will be translated based on user language)
DISCLAIMER_MESSAGE = """Hi — I'm ByOnco's Cancer Support Assistant. I can help you understand reports, treatment terms, and general care information. I can help you prepare questions for your oncologist. I'm not a doctor and I can't help with emergencies. If you agree to continue, reply: AGREE"""

NAME_PROMPT = "Thank you. What name should I use for you? (You can share your name or initials.)"

AGE_PROMPT = "What's your age? (This helps me provide age-appropriate information.)"

COUNTRY_PROMPT = "Which country are you in? (e.g., India, USA, UK)"

CITY_PROMPT = "Which city are you in? (This helps me find relevant hospitals and resources.)"

LANGUAGE_PROMPT = """What language would you prefer for our conversation?

Available languages:
English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Spanish, German, Russian, French, Portuguese, Japanese, Chinese

Please reply with the language name (e.g., "Hindi" or "English")."""

ONBOARDING_COMPLETE = """Great! I've saved your information. How can I help you right now?

1) Reports — Understand your medical reports and test results
2) Side effects & symptoms — Get information about treatment side effects
3) Nutrition — Cancer-friendly diet and nutrition guidance
4) Hospital & costs — Find hospitals and estimate treatment costs

Reply with 1/2/3/4 or just type your question."""

MAIN_MENU = """How can I help you right now?

1) Reports — Understand your medical reports and test results
2) Side effects & symptoms — Get information about treatment side effects
3) Nutrition — Cancer-friendly diet and nutrition guidance
4) Hospital & costs — Find hospitals and estimate treatment costs

Reply with 1/2/3/4 or just type your question."""

# Usage limits
MAX_TEXT_PROMPTS_PER_DAY = 2
MAX_FILE_ATTACHMENTS_PER_DAY = 1
PREMIUM_LINK = "https://www.byoncocare.com/second-opinion"

LIMIT_EXCEEDED_TEXT = f"""You've reached your daily limit for free messages.

Free tier limits:
• {MAX_TEXT_PROMPTS_PER_DAY} text prompts per day
• {MAX_FILE_ATTACHMENTS_PER_DAY} file attachment per day

For unlimited access and premium features, upgrade to ByOnco Premium:
{PREMIUM_LINK}

Your limits reset daily. You can continue tomorrow or upgrade now for immediate access."""

# Immediate acknowledgment message when user asks a question
ACKNOWLEDGMENT_MESSAGE = "Thank you for your question. I'm reviewing your query and preparing a comprehensive response. This may take 1-2 minutes. Please bear with me."

LIMIT_EXCEEDED_FILE = f"""You've reached your daily limit for file attachments.

Free tier limits:
• {MAX_TEXT_PROMPTS_PER_DAY} text prompts per day
• {MAX_FILE_ATTACHMENTS_PER_DAY} file attachment per day

For unlimited access and premium features, upgrade to ByOnco Premium:
{PREMIUM_LINK}

Your limits reset daily. You can continue tomorrow or upgrade now for immediate access."""

# Positive sentiment responses
POSITIVE_RESPONSES = [
    "You're very welcome! I'm glad I could help. Feel free to reach out anytime if you have more questions.",
    "It's my pleasure to assist you. I'm here whenever you need support or have questions about your cancer care journey.",
    "Thank you for your kind words. I'm always here to help you navigate your cancer care journey. Don't hesitate to reach out if you need anything.",
    "You're most welcome! I'm here to support you. If you have any other questions or concerns, feel free to ask anytime."
]

# Inactivity messages
INACTIVITY_CHECK_MESSAGE = "Hi! I noticed you haven't responded in a while. Is there anything else I can help you with today?"
GOODBYE_MESSAGE = "Thank you for using ByOnco. I'm always here to help whenever you need support. Take care, and feel free to reach out anytime. Goodbye!"


def normalize_language(lang_input: str) -> Optional[str]:
    """Normalize language input to language code"""
    lang_lower = lang_input.lower().strip()
    return LANGUAGE_CODES.get(lang_lower)


def is_positive_sentiment(message: str) -> bool:
    """
    Detect if message expresses positive sentiment (thanks, gratitude, appreciation).
    
    Args:
        message: User's message text
        
    Returns:
        True if message appears to be positive/thankful
    """
    message_lower = message.lower().strip()
    
    # Keywords indicating positive sentiment
    positive_keywords = [
        "thank", "thanks", "thank you", "thankyou",
        "grateful", "gratitude", "appreciate", "appreciation",
        "helpful", "great help", "very helpful",
        "wonderful", "amazing", "excellent", "perfect",
        "good job", "well done", "nice", "lovely",
        "bless you", "god bless", "appreciated",
        "dhanyavad", "shukriya", "abhari",  # Hindi/Marathi thanks
        "nandri", "dhanyavaad", "kritagnya"  # Tamil/Telugu thanks
    ]
    
    # Check if message contains positive keywords
    for keyword in positive_keywords:
        if keyword in message_lower:
            return True
    
    # Check for short positive messages (likely just thanks)
    if len(message_lower.split()) <= 5:
        if any(word in message_lower for word in ["ok", "okay", "fine", "good", "great", "nice"]):
            return True
    
    return False


def check_inactivity(wa_id: str) -> Optional[str]:
    """
    Check if user has been inactive for more than the timeout period.
    
    Args:
        wa_id: WhatsApp ID of user
        
    Returns:
        Inactivity message if timeout exceeded, None otherwise
    """
    last_activity = store.get_last_activity(wa_id)
    if not last_activity:
        return None
    
    now = datetime.now(timezone.utc)
    time_diff = now - last_activity
    
    # Check if inactive for more than timeout
    if time_diff > timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES):
        # Mark as inactive and return goodbye message
        logger.info(f"User {wa_id[:6]}**** inactive for {time_diff.total_seconds() / 60:.1f} minutes")
        return GOODBYE_MESSAGE
    
    # Check if approaching timeout (8-10 minutes) - send check message
    if timedelta(minutes=8) <= time_diff <= timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES):
        logger.info(f"User {wa_id[:6]}**** approaching inactivity timeout")
        return INACTIVITY_CHECK_MESSAGE
    
    return None


async def get_ai_response(
    user_query: str,
    user_profile: Dict,
    menu_selection: Optional[str] = None,
    file_content: Optional[str] = None
) -> str:
    """
    Get AI response from OpenAI using Second Opinion service
    This integrates the same cancer-focused AI used in the website
    
    Args:
        user_query: User's question/message
        user_profile: User profile dict with name, age, city, country, language
        menu_selection: Optional menu selection (1-4)
        file_content: Optional extracted text from uploaded medical report
    
    Returns:
        AI-generated response in user's preferred language
    """
    try:
        from second_opinion.service import SecondOpinionAIService
        
        # Initialize service
        ai_service = SecondOpinionAIService()
        
        # Build context-aware query
        context_parts = []
        
        if user_profile.get("name"):
            context_parts.append(f"Patient name: {user_profile['name']}")
        if user_profile.get("age"):
            context_parts.append(f"Age: {user_profile['age']}")
        if user_profile.get("city"):
            context_parts.append(f"City: {user_profile['city']}")
        if user_profile.get("country"):
            context_parts.append(f"Country: {user_profile['country']}")
        
        # Add menu context
        menu_context = {
            "1": "The user is asking about medical reports and test results.",
            "2": "The user is asking about treatment side effects and symptoms.",
            "3": "The user is asking about cancer-friendly nutrition and diet.",
            "4": "The user is asking about hospitals and treatment costs."
        }
        
        if menu_selection and menu_selection in menu_context:
            context_parts.append(menu_context[menu_selection])
        
        # Build enhanced query
        user_language = user_profile.get("language", "en")
        language_names = {
            "en": "English", "hi": "Hindi", "mr": "Marathi", "ta": "Tamil", "te": "Telugu",
            "bn": "Bengali", "gu": "Gujarati", "kn": "Kannada", "es": "Spanish", "de": "German",
            "ru": "Russian", "fr": "French", "pt": "Portuguese", "ja": "Japanese", "zh": "Chinese"
        }
        language_name = language_names.get(user_language, "English")
        
        enhanced_query = user_query
        if context_parts:
            context_str = "\n".join(context_parts)
            enhanced_query = f"""Context about the patient:
{context_str}

User's question: {user_query}

CRITICAL: You MUST respond in {language_name} language. Provide a helpful, empathetic response focused on cancer/oncology care in {language_name}."""
        
        # Call OpenAI with token limit
        result = await ai_service.chat(message=enhanced_query, file_content=file_content)
        ai_response = result.get("response", "I apologize, but I'm having trouble processing your request. Please try again.")
        
        # Enforce max response length (prevent overly long responses)
        MAX_RESPONSE_LENGTH = 2000  # characters
        if len(ai_response) > MAX_RESPONSE_LENGTH:
            ai_response = ai_response[:MAX_RESPONSE_LENGTH] + "\n\n[Response truncated for length. Please ask more specific questions if you need more details.]"
        
        # Note: OpenAI will respond in the requested language. 
        # In production, you can add translation service or use OpenAI's multilingual capabilities
        # For languages other than English, you could:
        # 1. Add language instruction to system prompt
        # 2. Use a translation API (Google Translate, DeepL)
        # 3. Use OpenAI's native multilingual support
        
        return ai_response
        
    except ImportError:
        logger.error("Second Opinion AI service not available")
        return "I'm currently unable to process your request. Please try again later or contact support."
    except Exception as e:
        logger.error(f"Error getting AI response: {e}", exc_info=True)
        return "I apologize, but I encountered an error. Please try rephrasing your question or contact support."


def get_response_for_user(wa_id: str, message_body: str) -> str:
    """
    Determine the appropriate response based on user state and message.
    Implements the conversation state machine.
    
    NOTE: This function is synchronous for now. When OpenAI integration is active,
    it will need to be made async and the caller (api_routes.py) will need to await it.
    
    Returns:
        Response message to send to user
    """
    user = store.get_user(wa_id)
    
    # User doesn't exist or hasn't consented
    if not user or not user.get("consented"):
        message_upper = message_body.upper().strip()
        if message_upper == "AGREE":
            store.mark_consented(wa_id)
            return NAME_PROMPT
        else:
            return DISCLAIMER_MESSAGE
    
    # User has consented, check onboarding step
    onboarding_step = user.get("onboarding_step", "none")
    profile = user.get("profile", {})
    
    if onboarding_step == "name":
        # Save name and ask for age
        name = message_body.strip()
        if name:
            store.set_profile_field(wa_id, "name", name)
            store.advance_onboarding(wa_id, "age")
            return AGE_PROMPT
        else:
            return "Please share your name or initials."
    
    elif onboarding_step == "age":
        # Save age and ask for country
        age = message_body.strip()
        if age:
            store.set_profile_field(wa_id, "age", age)
            store.advance_onboarding(wa_id, "country")
            return COUNTRY_PROMPT
        else:
            return "Please share your age."
    
    elif onboarding_step == "country":
        # Save country and ask for city
        country = message_body.strip()
        if country:
            store.set_profile_field(wa_id, "country", country)
            store.advance_onboarding(wa_id, "city")
            return CITY_PROMPT
        else:
            return "Please share your country."
    
    elif onboarding_step == "city":
        # Save city and ask for language
        city = message_body.strip()
        if city:
            store.set_profile_field(wa_id, "city", city)
            store.advance_onboarding(wa_id, "language")
            return LANGUAGE_PROMPT
        else:
            return "Please share your city."
    
    elif onboarding_step == "language":
        # Save language and complete onboarding
        lang_input = message_body.strip()
        lang_code = normalize_language(lang_input)
        
        if lang_code:
            store.set_profile_field(wa_id, "language", lang_code)
            store.complete_onboarding(wa_id)
            return ONBOARDING_COMPLETE
        else:
            return f"I didn't recognize that language. {LANGUAGE_PROMPT}"
    
    elif onboarding_step == "complete":
        # User is fully onboarded - handle menu selections or direct questions
        message_upper = message_body.upper().strip()
        
        # Handle menu selections
        if message_upper in ["1", "REPORTS"]:
            return "I can help you understand medical reports. Please share your report details or ask a specific question about it."
        elif message_upper in ["2", "SIDE EFFECTS", "SYMPTOMS"]:
            return "I can provide information about treatment side effects and symptoms. What would you like to know?"
        elif message_upper in ["3", "NUTRITION"]:
            return "I can help with cancer-friendly nutrition guidance. What specific nutrition question do you have?"
        elif message_upper in ["4", "HOSPITAL", "COSTS"]:
            return "I can help you find hospitals and estimate treatment costs. What type of treatment are you looking for?"
        else:
            # Direct question - will be handled by OpenAI in async version
            # For now, return menu
            return f"I understand you said: {message_body}\n\n{MAIN_MENU}"
    
    else:
        # Fallback - should not happen
        return MAIN_MENU


async def process_attachment_async(
    wa_id: str,
    media_id: str,
    mime_type: str,
    message_type: str,
    caption: Optional[str] = None
) -> Tuple[str, Optional[str], Optional[dict]]:
    """
    Process attachment (image or PDF) and extract text.
    
    Args:
        wa_id: WhatsApp ID of user
        media_id: Media ID from WhatsApp
        mime_type: MIME type of the media
        message_type: "image" or "document"
        caption: Optional caption from user
        
    Returns:
        Tuple of (response_message, extracted_text, metadata)
        extracted_text is None if extraction failed
        metadata includes extraction details and token usage
    """
    from .media_handler import download_media
    from .extractor import extract_text_from_media
    
    # Check for inactivity timeout BEFORE updating activity
    inactivity_msg = check_inactivity(wa_id)
    if inactivity_msg:
        if inactivity_msg == GOODBYE_MESSAGE:
            return inactivity_msg, None, None
        store.update_last_activity(wa_id)
        return inactivity_msg, None, None
    
    # Update last activity timestamp (user is active)
    store.update_last_activity(wa_id)
    
    # Check if user is onboarded
    user = store.get_user(wa_id)
    if not user or user.get("onboarding_step") != "complete":
        return "Please complete onboarding first by sending 'Hi' and following the setup process.", None, None
    
    # Check file attachment limit
    usage = store.get_usage(wa_id)
    if usage["file_attachments_today"] >= MAX_FILE_ATTACHMENTS_PER_DAY:
        return LIMIT_EXCEEDED_FILE, None, None
    
    # Download media
    logger.info(f"Downloading media: media_id={media_id[:20]}..., mime_type={mime_type}")
    file_bytes, downloaded_mime_type, file_size = await download_media(media_id)
    
    if not file_bytes:
        logger.error(f"Failed to download media: media_id={media_id[:20]}...")
        return "I couldn't download your file. Please try uploading again or check your internet connection.", None, None
    
    logger.info(f"Downloaded media: size={file_size} bytes, mime_type={downloaded_mime_type}")
    
    # Extract text
    logger.info(f"Extracting text from {message_type}...")
    extracted_text, success, extraction_metadata = extract_text_from_media(file_bytes, downloaded_mime_type)
    
    if not success or not extracted_text:
        logger.warning(f"Text extraction failed for media_id={media_id[:20]}...")
        return (
            "I couldn't read the text from your file. Please make sure:\n"
            "• The image is clear and well-lit\n"
            "• The PDF is not corrupted\n"
            "• Text is visible and not too blurry\n\n"
            "Try uploading a clearer photo or PDF.",
            None,
            None
        )
    
    logger.info(f"Successfully extracted {len(extracted_text)} characters from {message_type}")
    
    # Increment usage counter
    store.increment_file_attachment(wa_id)
    
    # Build prompt for AI
    user_query = caption or "Please analyze this medical report and provide: (a) report summary, (b) flagged values if obvious, (c) recommended questions for oncologist, (d) next-step guidance."
    
    # Get AI response with extracted text
    profile = user.get("profile", {})
    try:
        ai_response = await get_ai_response(user_query, profile, menu_selection="1", file_content=extracted_text)
        
        # Log token usage (if available from AI service)
        metadata = {
            "media_type": message_type,
            "file_size": file_size,
            "extraction_method": extraction_metadata.get("extraction_method"),
            "pages_processed": extraction_metadata.get("pages_processed", 0),
            "extracted_text_length": len(extracted_text)
        }
        
        return ai_response, extracted_text, metadata
        
    except Exception as e:
        logger.error(f"Error getting AI response for attachment: {e}", exc_info=True)
        return (
            "I successfully extracted text from your file, but encountered an error processing it. "
            "Please try again or contact support.",
            extracted_text,
            None
        )


async def get_response_for_user_async(wa_id: str, message_body: str) -> str:
    """
    Async version that integrates OpenAI for cancer support assistance.
    This is called after onboarding is complete and user asks questions.
    Includes safety guardrails: emergency detection, risky content filtering, cancer-only gating.
    
    Returns:
        Response message to send to user (AI-generated or menu)
    """
    from .safety import classify_message
    from .rate_limiter import rate_limiter
    
    # Check for inactivity timeout BEFORE updating activity (to detect if they were inactive)
    inactivity_msg = check_inactivity(wa_id)
    if inactivity_msg:
        # If goodbye message, don't update activity (conversation is ending)
        if inactivity_msg == GOODBYE_MESSAGE:
            return inactivity_msg
        # Otherwise, it's a check message - update activity and return it
        store.update_last_activity(wa_id)
        return inactivity_msg
    
    # Update last activity timestamp (user is active)
    store.update_last_activity(wa_id)
    
    # Handle RESET and DELETE commands
    message_upper = message_body.upper().strip()
    if message_upper in ["RESET", "RESTART", "START OVER"]:
        store.reset_user(wa_id)
        rate_limiter.reset(wa_id)
        store.update_last_activity(wa_id)
        return "Your data has been reset. Let's start fresh!\n\n" + DISCLAIMER_MESSAGE
    
    if message_upper in ["DELETE MY DATA", "DELETE DATA", "DELETE", "REMOVE MY DATA"]:
        store.delete_user(wa_id)
        rate_limiter.reset(wa_id)
        return "Your data has been deleted. If you'd like to start again, send 'Hi'."
    
    # Rate limiting check
    is_allowed, rate_limit_msg = rate_limiter.is_allowed(wa_id)
    if not is_allowed:
        return rate_limit_msg
    
    user = store.get_user(wa_id)
    
    # User doesn't exist or hasn't consented
    if not user or not user.get("consented"):
        message_upper = message_body.upper().strip()
        if message_upper == "AGREE":
            store.mark_consented(wa_id)
            return NAME_PROMPT
        else:
            return DISCLAIMER_MESSAGE
    
    # User has consented, check onboarding step
    onboarding_step = user.get("onboarding_step", "none")
    profile = user.get("profile", {})
    
    if onboarding_step == "name":
        name = message_body.strip()
        if name:
            store.set_profile_field(wa_id, "name", name)
            store.advance_onboarding(wa_id, "age")
            return AGE_PROMPT
        else:
            return "Please share your name or initials."
    
    elif onboarding_step == "age":
        age = message_body.strip()
        if age:
            store.set_profile_field(wa_id, "age", age)
            store.advance_onboarding(wa_id, "country")
            return COUNTRY_PROMPT
        else:
            return "Please share your age."
    
    elif onboarding_step == "country":
        country = message_body.strip()
        if country:
            store.set_profile_field(wa_id, "country", country)
            store.advance_onboarding(wa_id, "city")
            return CITY_PROMPT
        else:
            return "Please share your country."
    
    elif onboarding_step == "city":
        city = message_body.strip()
        if city:
            store.set_profile_field(wa_id, "city", city)
            store.advance_onboarding(wa_id, "language")
            return LANGUAGE_PROMPT
        else:
            return "Please share your city."
    
    elif onboarding_step == "language":
        lang_input = message_body.strip()
        lang_code = normalize_language(lang_input)
        
        if lang_code:
            store.set_profile_field(wa_id, "language", lang_code)
            store.complete_onboarding(wa_id)
            return ONBOARDING_COMPLETE
        else:
            return f"I didn't recognize that language. {LANGUAGE_PROMPT}"
    
    elif onboarding_step == "complete":
        # User is fully onboarded - use OpenAI for responses with safety checks
        
        # Check for positive sentiment (thanks, gratitude) - respond warmly
        if is_positive_sentiment(message_body):
            import random
            response = random.choice(POSITIVE_RESPONSES)
            logger.info(f"Detected positive sentiment from {wa_id[:6]}****, responding warmly")
            return response
        
        # USAGE LIMIT CHECK: Check daily limits before processing
        usage = store.get_usage(wa_id)
        if usage["text_prompts_today"] >= MAX_TEXT_PROMPTS_PER_DAY:
            return LIMIT_EXCEEDED_TEXT
        
        # SAFETY CHECK 1: Emergency detection (bypasses AI, returns urgent guidance)
        action, safety_response = classify_message(message_body)
        if action == "emergency":
            return safety_response
        if action == "risky":
            return safety_response
        if action == "non_cancer":
            return safety_response
        # action == "cancer_ok" - proceed to OpenAI
        
        message_upper = message_body.upper().strip()
        menu_selection = None
        
        # Check if it's a menu selection
        if message_upper in ["1", "REPORTS"]:
            menu_selection = "1"
            prompt = "I need help understanding medical reports and test results. "
        elif message_upper in ["2", "SIDE EFFECTS", "SYMPTOMS"]:
            menu_selection = "2"
            prompt = "I need information about treatment side effects and symptoms. "
        elif message_upper in ["3", "NUTRITION"]:
            menu_selection = "3"
            prompt = "I need cancer-friendly nutrition and diet guidance. "
        elif message_upper in ["4", "HOSPITAL", "COSTS"]:
            menu_selection = "4"
            prompt = "I need help finding hospitals and estimating treatment costs. "
        else:
            # Direct question - use as-is (already passed safety check)
            prompt = message_body
        
        # Increment usage counter (only if we're actually processing)
        store.increment_text_prompt(wa_id)
        
        # Return acknowledgment message immediately
        # The actual AI response will be sent in a follow-up message by api_routes.py
        return ACKNOWLEDGMENT_MESSAGE
    
    else:
        return MAIN_MENU
