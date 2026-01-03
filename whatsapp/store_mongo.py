"""
MongoDB-backed store for WhatsApp conversations
Replaces in-memory store with persistent storage
"""
from typing import Dict, Optional, Any
from datetime import datetime, timezone
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class MongoDBWhatsAppStore:
    """
    MongoDB-backed store for user state, processed messages, and opt-outs.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.processed_messages_collection = db.processed_message_ids
        self.user_state_collection = db.whatsapp_user_state
        self.user_prefs_collection = db.whatsapp_user_prefs
        self.user_optout_collection = db.whatsapp_user_optout
    
    async def initialize_indexes(self):
        """Create required indexes for performance and uniqueness"""
        try:
            # Unique index on message_id for idempotency
            await self.processed_messages_collection.create_index(
                "message_id",
                unique=True,
                name="message_id_unique"
            )
            
            # Index on wa_id for user state lookups
            await self.user_state_collection.create_index(
                "wa_id",
                unique=True,
                name="wa_id_unique"
            )
            
            # Index on wa_id for opt-out lookups
            await self.user_optout_collection.create_index(
                "wa_id",
                unique=True,
                name="optout_wa_id_unique"
            )
            
            # TTL index to auto-delete processed messages after 30 days
            await self.processed_messages_collection.create_index(
                "processed_at",
                expireAfterSeconds=2592000,  # 30 days
                name="processed_at_ttl"
            )
            
            logger.info("✅ MongoDB indexes created for WhatsApp store")
        
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}", exc_info=True)
    
    async def is_message_processed(self, message_id: str) -> bool:
        """Check if message was already processed (idempotency)"""
        try:
            doc = await self.processed_messages_collection.find_one(
                {"message_id": message_id}
            )
            return doc is not None
        except Exception as e:
            logger.error(f"Error checking message processed: {e}", exc_info=True)
            return False  # On error, assume not processed to avoid duplicates
    
    async def mark_message_processed(self, message_id: str):
        """Mark message as processed"""
        try:
            await self.processed_messages_collection.insert_one({
                "message_id": message_id,
                "processed_at": datetime.now(timezone.utc)
            })
        except Exception as e:
            # Ignore duplicate key errors (idempotency)
            if "duplicate" not in str(e).lower() and "E11000" not in str(e):
                logger.error(f"Error marking message processed: {e}", exc_info=True)
    
    async def get_user_state(self, wa_id: str) -> Optional[Dict[str, Any]]:
        """Get user state by WhatsApp ID"""
        try:
            doc = await self.user_state_collection.find_one({"wa_id": wa_id})
            if doc:
                doc.pop("_id", None)  # Remove MongoDB _id
                return doc
            return None
        except Exception as e:
            logger.error(f"Error getting user state: {e}", exc_info=True)
            return None
    
    async def create_user_state(self, wa_id: str) -> Dict[str, Any]:
        """Create new user with default state"""
        now = datetime.now(timezone.utc)
        user = {
            "wa_id": wa_id,
            "consented": False,
            "state": "consent",  # consent, intake, complete
            "step": None,  # Current intake step
            "collected_fields": {},
            "created_at": now,
            "updated_at": now
        }
        try:
            await self.user_state_collection.insert_one(user)
            logger.info(f"Created new user state for {wa_id[:6]}****")
            return user
        except Exception as e:
            logger.error(f"Error creating user state: {e}", exc_info=True)
            return user
    
    async def update_user_state(self, wa_id: str, **updates) -> Dict[str, Any]:
        """Update user state"""
        updates["updated_at"] = datetime.now(timezone.utc)
        try:
            result = await self.user_state_collection.find_one_and_update(
                {"wa_id": wa_id},
                {"$set": updates},
                return_document=True,
                upsert=True
            )
            if result:
                result.pop("_id", None)
                return result
            return await self.create_user_state(wa_id)
        except Exception as e:
            logger.error(f"Error updating user state: {e}", exc_info=True)
            return await self.get_user_state(wa_id) or await self.create_user_state(wa_id)
    
    async def save_user_prefs(self, wa_id: str, prefs: Dict[str, Any]):
        """Save final user preferences/intake answers"""
        prefs["wa_id"] = wa_id
        prefs["saved_at"] = datetime.now(timezone.utc)
        try:
            await self.user_prefs_collection.update_one(
                {"wa_id": wa_id},
                {"$set": prefs},
                upsert=True
            )
            logger.info(f"Saved user prefs for {wa_id[:6]}****")
        except Exception as e:
            logger.error(f"Error saving user prefs: {e}", exc_info=True)
    
    async def is_opted_out(self, wa_id: str) -> bool:
        """Check if user has opted out"""
        try:
            doc = await self.user_optout_collection.find_one({"wa_id": wa_id})
            return doc is not None and doc.get("opted_out", False)
        except Exception as e:
            logger.error(f"Error checking opt-out: {e}", exc_info=True)
            return False
    
    async def opt_out(self, wa_id: str):
        """Mark user as opted out"""
        try:
            await self.user_optout_collection.update_one(
                {"wa_id": wa_id},
                {"$set": {
                    "opted_out": True,
                    "opted_out_at": datetime.now(timezone.utc)
                }},
                upsert=True
            )
            logger.info(f"User {wa_id[:6]}**** opted out")
        except Exception as e:
            logger.error(f"Error opting out user: {e}", exc_info=True)
    
    async def opt_in(self, wa_id: str):
        """Remove opt-out (opt back in)"""
        try:
            await self.user_optout_collection.delete_one({"wa_id": wa_id})
            logger.info(f"User {wa_id[:6]}**** opted back in")
        except Exception as e:
            logger.error(f"Error opting in user: {e}", exc_info=True)

