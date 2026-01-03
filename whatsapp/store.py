"""
In-memory state store for WhatsApp conversations
Designed to be easily replaceable with PostgreSQL or MongoDB
"""
from typing import Dict, Optional, Set
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class WhatsAppStore:
    """
    In-memory store for user state and processed messages.
    Interface allows easy swap to database later.
    """
    
    def __init__(self):
        # users[wa_id] = {
        #   "consented": bool,
        #   "onboarding_step": str,  # "none", "name", "age", "city", "country", "language", "complete"
        #   "profile": {
        #     "name": str,
        #     "age": Optional[str],
        #     "city": Optional[str],
        #     "country": Optional[str],
        #     "language": Optional[str]  # "en", "hi", "mr", "ta", "te", "bn", "gu", "kn", "es", "de", "ru", "fr", "pt", "ja", "zh"
        #   },
        #   "usage": {
        #     "text_prompts_today": int,
        #     "file_attachments_today": int,
        #     "last_reset_date": str  # YYYY-MM-DD format
        #   },
        #   "created_at": datetime,
        #   "updated_at": datetime
        # }
        self.users: Dict[str, Dict] = {}
        
        # Track processed message IDs for idempotency
        self.processed_message_ids: Set[str] = set()
    
    def get_user(self, wa_id: str) -> Optional[Dict]:
        """Get user state by WhatsApp ID"""
        return self.users.get(wa_id)
    
    def create_user(self, wa_id: str) -> Dict:
        """Create new user with default state"""
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        user = {
            "consented": False,
            "onboarding_step": "none",
            "profile": {
                "name": None,
                "age": None,
                "city": None,
                "country": None,
                "language": None
            },
            "usage": {
                "text_prompts_today": 0,
                "file_attachments_today": 0,
                "last_reset_date": today
            },
            "created_at": now,
            "updated_at": now
        }
        self.users[wa_id] = user
        logger.info(f"Created new user: {wa_id}")
        return user
    
    def update_user(self, wa_id: str, **updates) -> Dict:
        """Update user state"""
        if wa_id not in self.users:
            self.create_user(wa_id)
        
        self.users[wa_id].update(updates)
        self.users[wa_id]["updated_at"] = datetime.now(timezone.utc)
        return self.users[wa_id]
    
    def mark_consented(self, wa_id: str) -> Dict:
        """Mark user as consented and start onboarding"""
        return self.update_user(
            wa_id,
            consented=True,
            onboarding_step="name"
        )
    
    def set_profile_field(self, wa_id: str, field: str, value: str) -> Dict:
        """Set a profile field (name, age, city, country, language)"""
        user = self.get_user(wa_id) or self.create_user(wa_id)
        user["profile"][field] = value
        user["updated_at"] = datetime.now(timezone.utc)
        return user
    
    def advance_onboarding(self, wa_id: str, next_step: str) -> Dict:
        """Move to next onboarding step"""
        return self.update_user(wa_id, onboarding_step=next_step)
    
    def complete_onboarding(self, wa_id: str) -> Dict:
        """Mark onboarding as complete"""
        return self.update_user(wa_id, onboarding_step="complete")
    
    def _reset_daily_usage_if_needed(self, wa_id: str):
        """Reset daily usage counters if it's a new day"""
        if wa_id not in self.users:
            return
        
        user = self.users[wa_id]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        last_reset = user.get("usage", {}).get("last_reset_date", today)
        
        if last_reset != today:
            # New day - reset counters
            if "usage" not in user:
                user["usage"] = {}
            user["usage"]["text_prompts_today"] = 0
            user["usage"]["file_attachments_today"] = 0
            user["usage"]["last_reset_date"] = today
            logger.info(f"Daily usage reset for {wa_id[:6]}****")
    
    def get_usage(self, wa_id: str) -> Dict[str, int]:
        """Get current daily usage for user"""
        self._reset_daily_usage_if_needed(wa_id)
        user = self.get_user(wa_id)
        if not user:
            return {"text_prompts_today": 0, "file_attachments_today": 0}
        
        usage = user.get("usage", {})
        return {
            "text_prompts_today": usage.get("text_prompts_today", 0),
            "file_attachments_today": usage.get("file_attachments_today", 0)
        }
    
    def increment_text_prompt(self, wa_id: str) -> int:
        """Increment text prompt counter and return new count"""
        self._reset_daily_usage_if_needed(wa_id)
        user = self.get_user(wa_id) or self.create_user(wa_id)
        
        if "usage" not in user:
            user["usage"] = {
                "text_prompts_today": 0,
                "file_attachments_today": 0,
                "last_reset_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            }
        
        user["usage"]["text_prompts_today"] = user["usage"].get("text_prompts_today", 0) + 1
        user["updated_at"] = datetime.now(timezone.utc)
        return user["usage"]["text_prompts_today"]
    
    def increment_file_attachment(self, wa_id: str) -> int:
        """Increment file attachment counter and return new count"""
        self._reset_daily_usage_if_needed(wa_id)
        user = self.get_user(wa_id) or self.create_user(wa_id)
        
        if "usage" not in user:
            user["usage"] = {
                "text_prompts_today": 0,
                "file_attachments_today": 0,
                "last_reset_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            }
        
        user["usage"]["file_attachments_today"] = user["usage"].get("file_attachments_today", 0) + 1
        user["updated_at"] = datetime.now(timezone.utc)
        return user["usage"]["file_attachments_today"]
    
    def reset_user(self, wa_id: str):
        """Reset user data (for RESET/DELETE commands)"""
        if wa_id in self.users:
            # Keep only minimal data: wa_id and language preference
            language = self.users[wa_id].get("profile", {}).get("language")
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            self.users[wa_id] = {
                "consented": False,
                "onboarding_step": "none",
                "profile": {
                    "name": None,
                    "age": None,
                    "city": None,
                    "country": None,
                    "language": language  # Preserve language preference
                },
                "usage": {
                    "text_prompts_today": 0,
                    "file_attachments_today": 0,
                    "last_reset_date": today
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            logger.info(f"User data reset for {wa_id[:6]}**** (language preserved)")
    
    def delete_user(self, wa_id: str):
        """Delete all user data (for DELETE MY DATA command)"""
        if wa_id in self.users:
            del self.users[wa_id]
            logger.info(f"User data deleted for {wa_id[:6]}****")
    
    def is_message_processed(self, message_id: str) -> bool:
        """Check if message was already processed (idempotency)"""
        return message_id in self.processed_message_ids
    
    def mark_message_processed(self, message_id: str):
        """Mark message as processed"""
        self.processed_message_ids.add(message_id)
        # Keep only last 10000 message IDs to prevent memory bloat
        if len(self.processed_message_ids) > 10000:
            # Remove oldest 1000 (simple FIFO)
            to_remove = list(self.processed_message_ids)[:1000]
            for msg_id in to_remove:
                self.processed_message_ids.discard(msg_id)


# Global store instance (in-memory)
# In production, replace with database-backed store
store = WhatsAppStore()
