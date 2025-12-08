"""
Service for Get Started form submissions
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from .models import GetStartedRequest, GetStartedSubmission
import logging
import uuid

logger = logging.getLogger(__name__)


class GetStartedService:
    """Service for handling Get Started form submissions"""
    
    def __init__(self, db):
        self.db = db
        self.submissions_collection = db.get_started_submissions
    
    async def create_submission(self, request: GetStartedRequest) -> Dict[str, Any]:
        """Create a new Get Started submission"""
        try:
            submission_doc = {
                "id": str(uuid.uuid4()),
                "full_name": request.full_name,
                "email": request.email.lower(),
                "phone": request.phone,
                "city": request.city,
                "state": request.state,
                "country": request.country,
                "cancer_type": request.cancer_type,
                "cancer_stage": request.cancer_stage,
                "has_insurance": request.has_insurance,
                "insurance_provider": request.insurance_provider,
                "insurance_policy_number": request.insurance_policy_number,
                "preferred_language": request.preferred_language,
                "preferred_contact_method": request.preferred_contact_method,
                "preferred_time": request.preferred_time,
                "additional_notes": request.additional_notes,
                "agree_to_terms": request.agree_to_terms,
                "agree_to_contact": request.agree_to_contact,
                "status": "pending_review",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.submissions_collection.insert_one(submission_doc)
            
            return {
                "id": submission_doc["id"],
                "message": "Thank you for your submission! We'll contact you soon.",
                "submitted_at": submission_doc["created_at"],
                "status": "pending_review"
            }
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise
    
    async def get_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get a submission by ID"""
        try:
            submission = await self.submissions_collection.find_one({"id": submission_id})
            if submission:
                return dict(submission)
            return None
        except Exception as e:
            logger.error(f"Error getting submission: {str(e)}")
            raise
    
    async def get_all_submissions(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all submissions with optional filtering"""
        try:
            query = {}
            if status:
                query["status"] = status
            
            submissions = await self.submissions_collection.find(query).sort("created_at", -1).limit(limit).to_list(limit)
            return [dict(sub) for sub in submissions]
        except Exception as e:
            logger.error(f"Error getting submissions: {str(e)}")
            raise
    
    async def update_submission_status(
        self,
        submission_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update submission status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            if notes:
                update_data["admin_notes"] = notes
            
            result = await self.submissions_collection.update_one(
                {"id": submission_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating submission: {str(e)}")
            raise

