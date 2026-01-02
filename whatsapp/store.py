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
        #   "onboarding_step": str,  # "none", "name", "age", "city", "complete"
        #   "profile": {
        #     "name": str,
        #     "age": Optional[str],
        #     "city": Optional[str]
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
        user = {
            "consented": False,
            "onboarding_step": "none",
            "profile": {
                "name": None,
                "age": None,
                "city": None
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
        """Set a profile field (name, age, city)"""
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

