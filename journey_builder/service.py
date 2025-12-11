"""
Service for Journey Builder AI operations using OpenAI
"""
import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

# System prompt for Journey Builder
JOURNEY_BUILDER_SYSTEM_PROMPT = """You are ByOnco Journey Builder, an AI assistant specialized in medical tourism planning for oncology patients.

Your role is to help patients plan their medical journey by:
1. Extracting key information from their free-text description (cancer type, stage, origin city, destination preferences, budget)
2. Generating 3 journey packages (Value, Balanced, Comfort) with realistic costs, hospitals, and logistics
3. Providing optimization suggestions

IMPORTANT: You must respond ONLY with valid JSON matching this exact structure:

{
  "profile": {
    "cancerType": "e.g., Lung Cancer",
    "stage": "e.g., Stage III",
    "originDest": "e.g., BLR → DEL / BOM",
    "estBudget": "e.g., ₹15L – ₹20L INR"
  },
  "plans": [
    {
      "planType": "Value",
      "city": "Mumbai",
      "region": "Maharashtra",
      "priceRange": "₹12L – ₹15L",
      "duration": "~6 weeks duration",
      "hospitalName": "Tata Memorial Centre",
      "hospitalNote": "Govt-aided, high volume, premier oncology research institute.",
      "bullets": [
        "Chemo-Radiation protocol (General Ward)",
        "Round-trip Train (AC 2 Tier) for 3",
        "Guest House / Budget Lodge (40 nights)"
      ],
      "fitNote": "Best for maximizing medical quality on a strict budget. Wait times may be higher.",
      "overBudget": false,
      "icon": "lucide:train-front"
    },
    {
      "planType": "Balanced",
      "city": "New Delhi",
      "region": "Delhi NCR",
      "priceRange": "₹16L – ₹19L",
      "duration": "~5 weeks duration",
      "hospitalName": "Max Super Speciality",
      "hospitalNote": "NABH accredited, specialized Thoracic Oncology team.",
      "bullets": [
        "Surgery + Chemo (Twin Sharing Room)",
        "Domestic Flights (Economy) for 2",
        "3-Star Hotel / Serviced Apt (30 nights)",
        "ByOnco Care Coordinator included"
      ],
      "fitNote": "Good balance of comfort, speed, and cost. Within your upper budget limit.",
      "overBudget": false,
      "icon": "lucide:plane"
    },
    {
      "planType": "Comfort",
      "city": "Gurugram",
      "region": "NCR",
      "priceRange": "₹22L – ₹25L",
      "duration": "~5 weeks duration",
      "hospitalName": "Medanta - The Medicity",
      "hospitalNote": "JCI accredited, advanced robotic surgery options.",
      "bullets": [
        "Robotic Surgery + Targeted Therapy (Private)",
        "Flexi Flights + Airport Transfer",
        "4-Star Hotel near hospital (30 nights)",
        "24/7 Dedicated Concierge"
      ],
      "fitNote": "Maximum comfort and reduced logistics burden, but exceeds stated budget.",
      "overBudget": true,
      "icon": "lucide:armchair"
    }
  ],
  "suggestions": {
    "items": [
      {
        "title": "Reduce Costs",
        "text": "Opt for train travel to Delhi instead of flights to save approx ₹15,000."
      },
      {
        "title": "Accommodation",
        "text": "Staying with relatives in Delhi/Mumbai can reduce the package cost by ₹60,000–₹1L."
      }
    ]
  },
  "disclaimer": "I'm sorry to hear about your father's diagnosis. Based on your request, I have structured a journey plan focusing on **Stage III Lung Cancer** treatment in **Mumbai or Delhi**, keeping within the **₹15–20 Lakhs** budget range."
}

GUIDELINES:
- Use real Indian cities and hospitals (Mumbai, Delhi, Bangalore, Chennai, etc.)
- Value Plan: Government or budget-friendly hospitals, train travel, budget accommodation
- Balanced Plan: Mid-tier private hospitals, flights, 3-star hotels, within budget
- Comfort Plan: Premium hospitals, flexible travel, 4-star+ hotels, may exceed budget
- Prices should be realistic for Indian medical tourism (₹10L-₹30L range typically)
- Include medical treatment, travel, and accommodation in each plan
- Mark plans as overBudget: true if they exceed the user's stated budget
- Provide 2-3 practical suggestions for cost optimization
- Be empathetic and professional in the disclaimer message

Return ONLY the JSON, no additional text or markdown formatting."""


class JourneyBuilderService:
    """Service for journey builder AI operations"""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Using GPT-4o as specified
    
    async def build_journey(self, user_message: str) -> Dict[str, Any]:
        """
        Build a journey plan using OpenAI based on user's message
        
        Args:
            user_message: User's free-text description of their medical journey needs
            
        Returns:
            Dictionary matching JourneyResponse structure
        """
        try:
            # Call OpenAI Chat Completions API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": JOURNEY_BUILDER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Extract the JSON response
            content = response.choices[0].message.content
            
            # Parse JSON
            try:
                journey_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response: {e}")
                logger.error(f"Response content: {content}")
                # Return a fallback response
                return self._get_fallback_response(user_message)
            
            # Validate and return the structured response
            return journey_data
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # Return fallback response on error
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """
        Return a fallback response when OpenAI API fails
        """
        return {
            "profile": {
                "cancerType": "Unable to extract",
                "stage": "Unable to extract",
                "originDest": "Unable to extract",
                "estBudget": "Unable to extract"
            },
            "plans": [],
            "suggestions": {
                "items": [
                    {
                        "title": "Service Temporarily Unavailable",
                        "text": "We're experiencing technical difficulties. Please try again in a few moments or contact our support team."
                    }
                ]
            },
            "disclaimer": "I apologize, but I'm currently unable to process your request. Please try again or contact ByOnco support for assistance."
        }

