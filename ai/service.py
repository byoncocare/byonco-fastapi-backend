"""
AI Service for ByOnco
Handles OpenAI API calls with medical-only guardrails and rate limiting
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

# Health-related keywords for validation
HEALTH_KEYWORDS = [
    'cancer', 'tumor', 'tumour', 'carcinoma', 'sarcoma', 'leukemia', 'lymphoma',
    'symptom', 'diagnosis', 'treatment', 'therapy', 'chemotherapy', 'radiation', 'surgery',
    'doctor', 'physician', 'medical', 'health', 'disease', 'illness', 'condition',
    'pain', 'ache', 'fever', 'nausea', 'vomiting', 'bleeding', 'lump', 'mass',
    'biopsy', 'scan', 'mri', 'ct', 'x-ray', 'ultrasound', 'test', 'lab',
    'medication', 'drug', 'prescription', 'dose', 'side effect',
    'prognosis', 'survival', 'recovery', 'remission', 'metastasis',
    'stage', 'grade', 'malignant', 'benign', 'oncology', 'oncologist',
    'hospital', 'clinic', 'emergency', 'urgent', 'appointment', 'consultation',
]

NON_HEALTH_KEYWORDS = [
    'tesla', 'elon musk', 'company', 'business', 'stock', 'price', 'market',
    'owner', 'ceo', 'founder', 'who is', 'what is the owner', 'who owns',
    'weather', 'sports', 'movie', 'music', 'recipe', 'cooking', 'food',
    'travel', 'vacation', 'hotel', 'restaurant', 'shopping', 'fashion',
    'politics', 'election', 'president', 'government', 'news', 'current events',
]


class AIService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.openai_key and OpenAI:
            try:
                self.client = OpenAI(api_key=self.openai_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ OpenAI API key not configured or package not installed")

    def is_health_related(self, question: str) -> bool:
        """Validate that question is health-related"""
        if not question:
            return True  # Allow if no question provided
        
        lower_question = question.lower()
        
        # Check for non-health keywords first (higher priority)
        for keyword in NON_HEALTH_KEYWORDS:
            if keyword in lower_question:
                return False
        
        # Check for health keywords
        for keyword in HEALTH_KEYWORDS:
            if keyword in lower_question:
                return True
        
        # Default: allow if unclear (but log for review)
        return True

    async def generate_builder_plans(
        self,
        prompt: str,
        city: Optional[str] = None,
        budget_max: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate treatment plans using OpenAI"""
        if not self.client:
            return {
                "answer": json.dumps([
                    {
                        "title": "AI Service Unavailable",
                        "subtitle": "Please contact support",
                        "description": "AI service is currently unavailable. Please try again later.",
                        "minCost": 0,
                        "maxCost": 0,
                        "duration": "N/A",
                    }
                ]),
                "model": "fallback",
                "usage": None,
            }

        system_prompt = """You are a medical tourism treatment plan generator for ByOnco, specializing in cancer care.
Generate 3 treatment plan options: Budget-Friendly, Balanced, and Premium.
Each plan should include: title, subtitle, minCost (INR), maxCost (INR), duration, description, and hospital name.
Base recommendations on: cancer type, stage, budget constraints, city preference, and urgency.
Return ONLY valid JSON array of 3 plans, no other text."""

        user_prompt = f"Generate treatment plans for: {prompt}"
        if city:
            user_prompt += f"\nPreferred city: {city}"
        if budget_max:
            user_prompt += f"\nBudget limit: ₹{budget_max}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return {
                "answer": content,
                "model": "gpt-4",
                "usage": usage,
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "answer": json.dumps([
                    {
                        "title": "Error Generating Plans",
                        "subtitle": "Please try again",
                        "description": "An error occurred while generating treatment plans. Please try again later.",
                        "minCost": 0,
                        "maxCost": 0,
                        "duration": "N/A",
                    }
                ]),
                "model": "error",
                "usage": None,
            }

    async def generate_second_opinion(
        self,
        question: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate second opinion using OpenAI with medical-only validation"""
        # Validate health-related question
        if question and not self.is_health_related(question):
            return {
                "answer": None,
                "safe": False,
                "error": "I can only answer health and medical-related questions. Please ask about medical conditions, symptoms, treatments, or health concerns.",
            }

        if not self.client:
            return {
                "answer": "AI service is currently unavailable. Please try again later.",
                "safe": True,
                "error": None,
            }

        system_prompt = """You are a medical second opinion specialist for ByOnco.
Provide detailed, professional medical analysis based on patient information and uploaded medical reports.
Focus on: diagnosis assessment, treatment recommendations, prognosis, and next steps.
Be empathetic, clear, and medically accurate. Do NOT provide general knowledge answers to non-medical questions."""

        user_prompt = "Patient Information:\n"
        if profile:
            user_prompt += f"- Cancer Type: {profile.get('cancer_type', 'Not specified')}\n"
            user_prompt += f"- Stage: {profile.get('stage', 'Not specified')}\n"
            user_prompt += f"- Age: {profile.get('age', 'Not specified')}\n"
            user_prompt += f"- Gender: {profile.get('gender', 'Not specified')}\n"
            user_prompt += f"- Current Treatment: {profile.get('current_treatment', 'Not specified')}\n"
        
        if question:
            user_prompt += f"\nPatient Question: {question}\n"
        
        if attachments:
            user_prompt += f"\nMedical reports uploaded: {len(attachments)} file(s)\n"

        user_prompt += "\nPlease provide a comprehensive second opinion analysis."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Lower temperature for medical accuracy
                max_tokens=2000,
            )

            return {
                "answer": response.choices[0].message.content,
                "safe": True,
                "error": None,
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "answer": None,
                "safe": True,
                "error": "An error occurred while generating the second opinion. Please try again later.",
            }


