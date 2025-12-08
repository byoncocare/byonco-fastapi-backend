"""
Business logic for Rare Cancers API
"""
from typing import List, Optional, Dict, Any
from .seed_data import RARE_CANCERS, ALL_CANCERS, RARE_CANCER_DETAILS, RARE_CANCER_SPECIALISTS
import uuid


class RareCancersService:
    """Service class for rare cancer-related operations"""
    
    def __init__(self):
        self.rare_cancers = RARE_CANCERS
        self.all_cancers = ALL_CANCERS
        self.rare_cancer_details = RARE_CANCER_DETAILS
        self.rare_cancer_specialists = RARE_CANCER_SPECIALISTS
    
    def get_all_rare_cancers(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all rare cancers with optional filtering by category.
        Categories: ultra-rare, very-rare, rare
        """
        cancers = self.rare_cancers.copy()
        
        if category:
            cancers = [c for c in cancers if c.get("category") == category]
        
        # Add IDs and format for frontend
        result = []
        for cancer in cancers:
            cancer_data = {
                "id": str(uuid.uuid4()),
                "name": cancer.get("name", ""),
                "category": cancer.get("category", "rare"),
                "type": cancer.get("type", ""),
                "description": self.rare_cancer_details.get(
                    cancer.get("name", ""),
                    {}
                ).get("description", f"Rare cancer type: {cancer.get('type', '')}")
            }
            result.append(cancer_data)
        
        return result
    
    def get_rare_cancer_by_name(self, cancer_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific rare cancer"""
        # Find the cancer in the list
        cancer = None
        for c in self.rare_cancers:
            if c.get("name") == cancer_name:
                cancer = c
                break
        
        if not cancer:
            return None
        
        # Get additional details
        details = self.rare_cancer_details.get(cancer_name, {})
        
        return {
            "id": str(uuid.uuid4()),
            "name": cancer.get("name", ""),
            "category": cancer.get("category", "rare"),
            "type": cancer.get("type", ""),
            "description": details.get("description", f"Rare cancer type: {cancer.get('type', '')}"),
            "symptoms": details.get("symptoms", []),
            "treatment_options": details.get("treatment_options", []),
            "prognosis": details.get("prognosis", "Consult with specialist"),
            "research_status": details.get("research_status", "Active research ongoing"),
            "specialized_centers": self._get_specialized_centers(cancer.get("name", "")),
            "specialists": self.get_specialists_for_cancer(cancer_name),
            "clinical_trials": []
        }
    
    def _get_specialized_centers(self, cancer_name: str) -> List[Dict[str, Any]]:
        """Get specialized centers that treat this rare cancer"""
        # This would ideally come from a database or more detailed mapping
        # For now, return centers that might treat rare cancers
        centers = [
            {
                "name": "Tata Memorial Centre",
                "city": "Mumbai",
                "specialization": "Pediatric Oncology, Rare Cancers",
                "contact": "+91-22-2417-7000"
            },
            {
                "name": "AIIMS Cancer Centre",
                "city": "Delhi",
                "specialization": "All Cancer Types, Research Trials",
                "contact": "+91-11-2658-8500"
            }
        ]
        return centers
    
    # -------------------------
    # Specialists helpers
    # -------------------------

    def get_specialists_for_cancer(self, cancer_name: str) -> List[Dict[str, Any]]:
        """Return specialists mapped to a specific rare cancer name."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Looking for specialists for: '{cancer_name}'")
        logger.info(f"Available cancer types in specialists dict: {list(self.rare_cancer_specialists.keys())[:5]}...")
        
        # Try exact match first
        if cancer_name in self.rare_cancer_specialists:
            result = self.rare_cancer_specialists[cancer_name]
            logger.info(f"Found {len(result)} specialists with exact match")
            return result
        
        # Try case-insensitive match
        cancer_name_lower = cancer_name.lower().strip()
        for key in self.rare_cancer_specialists.keys():
            if key.lower().strip() == cancer_name_lower:
                result = self.rare_cancer_specialists[key]
                logger.info(f"Found {len(result)} specialists with case-insensitive match: '{key}'")
                return result
        
        # Try partial match (in case of slight variations)
        for key in self.rare_cancer_specialists.keys():
            key_lower = key.lower().strip()
            if cancer_name_lower in key_lower or key_lower in cancer_name_lower:
                result = self.rare_cancer_specialists[key]
                logger.info(f"Found {len(result)} specialists with partial match: '{key}'")
                return result
        
        logger.warning(f"No specialists found for: '{cancer_name}'")
        return []

    def get_all_specialists(
        self,
        name: Optional[str] = None,
        cancer_name: Optional[str] = None,
        region: Optional[str] = None,
        min_experience: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Flatten all rare-cancer specialists into a single list.
        Supports light filtering for the Find Oncologists page.
        """
        results: List[Dict[str, Any]] = []
        name_q = name.lower() if name else None
        cancer_q = cancer_name.lower() if cancer_name else None
        region_q = region.lower() if region else None

        for cancer, specialists in self.rare_cancer_specialists.items():
            for doc in specialists:
                entry = {
                    **doc,
                    "cancer_name": cancer,
                }
                if name_q and name_q not in doc.get("name", "").lower():
                    continue
                if cancer_q and cancer_q not in cancer.lower():
                    continue
                if region_q and region_q != doc.get("region", "").lower():
                    continue
                if min_experience is not None and doc.get("experience_years", 0) < min_experience:
                    continue
                results.append(entry)

        return results
    
    def get_cancers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all cancers in a specific category"""
        return self.get_all_rare_cancers(category=category)
    
    def search_rare_cancers(self, query: str) -> List[Dict[str, Any]]:
        """Search rare cancers by name or type"""
        query_lower = query.lower()
        results = []
        
        for cancer in self.rare_cancers:
            if (query_lower in cancer.get("name", "").lower() or 
                query_lower in cancer.get("type", "").lower()):
                results.append({
                    "id": str(uuid.uuid4()),
                    "name": cancer.get("name", ""),
                    "category": cancer.get("category", "rare"),
                    "type": cancer.get("type", "")
                })
        
        return results

