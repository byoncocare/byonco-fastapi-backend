"""
Message templates and conversation flow logic for ByOnco Cancer Copilot
Implements full intake flow with 6 essentials and recommendations
"""
from typing import Dict, Optional, Tuple
from .store_mongo import MongoDBWhatsAppStore
import logging

logger = logging.getLogger(__name__)


# Message templates
DISCLAIMER_MESSAGE = """Hi — I'm ByOnco's Cancer Support Assistant. I can help you find the right hospitals, doctors, and treatment options for your cancer care journey.

I'm not a doctor and I can't help with emergencies. If you agree to continue, reply: AGREE"""

STOP_MESSAGE = """You've opted out of messages. Reply START to receive messages again."""

START_MESSAGE = """Welcome back! You're now receiving messages again."""

HELP_MESSAGE = """I'm ByOnco's Cancer Support Assistant. I can help you:
• Find hospitals and doctors
• Understand treatment costs
• Get second opinions
• Find labs and diagnostic centers

Reply AGREE to get started, or STOP to opt out."""

# Intake questions (6 essentials)
INTAKE_QUESTIONS = {
    "cancer_type": "What type of cancer are you or your loved one dealing with? (e.g., Breast cancer, Lung cancer, Leukemia)",
    "stage": "What stage is the cancer? (If you don't know, reply 'Not sure' or 'Unknown')",
    "location": "Which city are you in, and how far are you willing to travel? (e.g., 'Mumbai, up to 500 km')",
    "budget": "What's your budget or insurance scheme? (e.g., '5 lakhs', 'Ayushman Bharat', 'Private insurance', 'Not sure')",
    "urgency": "How urgent is this? (e.g., 'Within 1 week', 'Within 1 month', 'Planning ahead')",
    "need": "What do you need most right now?\n1) Hospital recommendation\n2) Doctor consultation\n3) Second opinion\n4) Lab/diagnostic tests\n\nReply 1, 2, 3, or 4"
}

# Step order
INTAKE_STEPS = ["cancer_type", "stage", "location", "budget", "urgency", "need"]


def mask_phone(wa_id: str) -> str:
    """Mask phone number for logging (show last 4 digits only)"""
    if len(wa_id) > 4:
        return f"****{wa_id[-4:]}"
    return "****"


async def get_response_for_user(
    store: MongoDBWhatsAppStore,
    wa_id: str,
    message_body: str
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Async implementation of response logic"""
    
    message_upper = message_body.upper().strip()
    masked_id = mask_phone(wa_id)
    
    # Check opt-out status
    is_opted_out = await store.is_opted_out(wa_id)
    
    # Handle STOP/START/HELP commands (case-insensitive)
    if message_upper == "STOP":
        await store.opt_out(wa_id)
        logger.info(f"User {masked_id} opted out")
        return (STOP_MESSAGE, None)
    
    if message_upper == "START":
        await store.opt_in(wa_id)
        logger.info(f"User {masked_id} opted back in")
        return (START_MESSAGE, None)
    
    if message_upper in ["HELP", "INFO"]:
        return (HELP_MESSAGE, None)
    
    # If opted out and not START/HELP, don't respond
    if is_opted_out:
        logger.info(f"Ignoring message from opted-out user {masked_id}")
        return (STOP_MESSAGE, None)
    
    # Get or create user state
    user = await store.get_user_state(wa_id)
    if not user:
        user = await store.create_user_state(wa_id)
    
    state = user.get("state", "consent")
    step = user.get("step")
    collected = user.get("collected_fields", {})
    
    # Consent gate
    if state == "consent":
        if message_upper == "AGREE":
            await store.update_user_state(wa_id, consented=True, state="intake", step=INTAKE_STEPS[0])
            logger.info(f"User {masked_id} consented, starting intake")
            return (INTAKE_QUESTIONS[INTAKE_STEPS[0]], None)
        else:
            return (DISCLAIMER_MESSAGE, None)
    
    # Intake flow
    if state == "intake":
        current_step_index = INTAKE_STEPS.index(step) if step in INTAKE_STEPS else 0
        
        # Save current answer
        if current_step_index < len(INTAKE_STEPS):
            collected[step] = message_body.strip()
            await store.update_user_state(
                wa_id,
                collected_fields=collected,
                step=step
            )
            logger.info(f"User {masked_id} answered {step}: {message_body[:50]}")
        
        # Move to next step
        next_index = current_step_index + 1
        
        if next_index < len(INTAKE_STEPS):
            next_step = INTAKE_STEPS[next_index]
            await store.update_user_state(wa_id, step=next_step)
            return (INTAKE_QUESTIONS[next_step], None)
        else:
            # All steps complete - generate recommendations
            await store.update_user_state(wa_id, state="complete")
            
            # Generate recommendations (placeholder rules-based for now)
            recommendations = generate_recommendations(collected)
            
            # Save user preferences
            prefs = {
                "cancer_type": collected.get("cancer_type"),
                "stage": collected.get("stage"),
                "location": collected.get("location"),
                "budget": collected.get("budget"),
                "urgency": collected.get("urgency"),
                "need": collected.get("need")
            }
            await store.save_user_prefs(wa_id, prefs)
            
            logger.info(f"User {masked_id} completed intake, generated {len(recommendations)} recommendations")
            return (recommendations, prefs)
    
    # User is in "complete" state - show menu or handle queries
    if state == "complete":
        if message_upper in ["1", "HOSPITAL", "HOSPITALS"]:
            return ("I can help you find hospitals. Based on your previous intake, here are some options:\n\n" + 
                   generate_recommendations(collected), None)
        elif message_upper in ["2", "DOCTOR", "DOCTORS"]:
            return ("I can help you find doctors. Please share more details about the type of doctor you need.", None)
        elif message_upper in ["3", "SECOND OPINION", "OPINION"]:
            return ("I can help you get a second opinion. Please share your current diagnosis or reports.", None)
        elif message_upper in ["4", "LAB", "LABS", "DIAGNOSTIC"]:
            return ("I can help you find labs and diagnostic centers. What type of test do you need?", None)
        elif message_upper == "AGREE":
            # Restart intake
            await store.update_user_state(wa_id, state="intake", step=INTAKE_STEPS[0], collected_fields={})
            return (INTAKE_QUESTIONS[INTAKE_STEPS[0]], None)
        else:
            return ("How can I help you?\n\n1) Find hospitals\n2) Find doctors\n3) Get second opinion\n4) Find labs\n\nOr reply AGREE to start a new intake.", None)
    
    # Fallback
    return (DISCLAIMER_MESSAGE, None)


def generate_recommendations(collected: Dict[str, str]) -> str:
    """
    Generate recommendations based on collected intake data.
    Placeholder rules-based implementation (can be replaced with AI/ML later).
    """
    cancer_type = collected.get("cancer_type", "").lower()
    location = collected.get("location", "").lower()
    budget = collected.get("budget", "").lower()
    need = collected.get("need", "")
    
    recommendations = []
    
    # Basic recommendations based on cancer type and location
    if "mumbai" in location or "maharashtra" in location:
        recommendations.append("🏥 Tata Memorial Hospital, Mumbai - Premier cancer center")
        recommendations.append("🏥 Kokilaben Dhirubhai Ambani Hospital, Mumbai")
    
    if "delhi" in location or "ncr" in location:
        recommendations.append("🏥 AIIMS, New Delhi - Government hospital")
        recommendations.append("🏥 Apollo Hospitals, Delhi")
    
    if "bangalore" in location or "bengaluru" in location or "karnataka" in location:
        recommendations.append("🏥 HCG Cancer Centre, Bangalore")
        recommendations.append("🏥 Manipal Hospitals, Bangalore")
    
    if "chennai" in location or "tamil nadu" in location:
        recommendations.append("🏥 Apollo Hospitals, Chennai")
        recommendations.append("🏥 Adyar Cancer Institute, Chennai")
    
    # Add generic recommendations if location-specific not found
    if not recommendations:
        recommendations.append("🏥 Tata Memorial Hospital, Mumbai")
        recommendations.append("🏥 AIIMS, New Delhi")
        recommendations.append("🏥 Apollo Hospitals (Multiple cities)")
    
    # Budget considerations
    if "ayushman" in budget or "government" in budget or "free" in budget:
        recommendations.append("💡 Consider government hospitals for cost-effective care")
    
    # Need-based recommendations
    if need == "1" or "hospital" in need.lower():
        recommendations.append("💡 I can connect you with a coordinator to discuss hospital options in detail")
    
    # Format response
    response = "Based on your information, here are my recommendations:\n\n"
    response += "\n".join(recommendations[:5])  # Limit to 5 recommendations
    response += "\n\n💬 Would you like to talk to a coordinator? Reply 'YES' or ask me any questions."
    
    return response
