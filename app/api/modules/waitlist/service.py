"""
Service for Medical Tourism Waitlist operations
"""
from typing import Dict, Any
from datetime import datetime, timezone
import secrets
import logging

logger = logging.getLogger(__name__)


class WaitlistService:
    """Service for waitlist operations"""
    
    def __init__(self, db):
        self.db = db
        self.waitlist_collection = db.medical_tourism_waitlist
    
    async def add_to_waitlist(self, waitlist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a user to the medical tourism waitlist"""
        waitlist_id = str(secrets.token_urlsafe(16))
        
        waitlist_doc = {
            "id": waitlist_id,
            **waitlist_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.waitlist_collection.insert_one(waitlist_doc)
        
        return {
            "id": waitlist_id,
            "message": "Successfully added to waitlist",
            "created_at": waitlist_doc["created_at"]
        }

