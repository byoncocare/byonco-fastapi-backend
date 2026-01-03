"""
Message templates and conversation flow logic for ByOnco Cancer Copilot
All messages are original ByOnco branding (not copied from August AI)
"""
from typing import Dict, Optional
from .store import store


# Message templates
DISCLAIMER_MESSAGE = """Hi — I'm ByOnco's Cancer Support Assistant. I can help you understand reports, treatment terms, and general care information. I'm not a doctor and I can't help with emergencies. If you agree to continue, reply: AGREE"""

NAME_PROMPT = "Thank you. What name should I use for you? (You can share your name or initials.)"

AGE_PROMPT = "What's your age? (This helps me provide age-appropriate information.)"

CITY_PROMPT = "Which city or state are you in? (This helps me find relevant hospitals and resources.)"

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


def get_response_for_user(wa_id: str, message_body: str) -> str:
    """
    Determine the appropriate response based on user state and message.
    Implements the conversation state machine.
    
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
        # Save age and ask for city
        age = message_body.strip()
        if age:
            store.set_profile_field(wa_id, "age", age)
            store.advance_onboarding(wa_id, "city")
            return CITY_PROMPT
        else:
            return "Please share your age."
    
    elif onboarding_step == "city":
        # Save city and complete onboarding
        city = message_body.strip()
        if city:
            store.set_profile_field(wa_id, "city", city)
            store.complete_onboarding(wa_id)
            return ONBOARDING_COMPLETE
        else:
            return "Please share your city or state."
    
    elif onboarding_step == "complete":
        # User is fully onboarded - show main menu or handle menu selections
        message_upper = message_body.upper().strip()
        
        # Handle menu selections
        if message_upper in ["1", "REPORTS"]:
            return "I can help you understand medical reports. Please share your report or ask a specific question about it."
        elif message_upper in ["2", "SIDE EFFECTS", "SYMPTOMS"]:
            return "I can provide information about treatment side effects and symptoms. What would you like to know?"
        elif message_upper in ["3", "NUTRITION"]:
            return "I can help with cancer-friendly nutrition guidance. What specific nutrition question do you have?"
        elif message_upper in ["4", "HOSPITAL", "COSTS"]:
            return "I can help you find hospitals and estimate treatment costs. What type of treatment are you looking for?"
        else:
            # Echo user message and show menu
            return f"I understand you said: {message_body}\n\n{MAIN_MENU}"
    
    else:
        # Fallback - should not happen
        return MAIN_MENU
