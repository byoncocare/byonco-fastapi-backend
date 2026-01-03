"""
Service for Second Opinion AI operations using OpenAI
Restricted to health, treatment, and oncology-related queries only
"""
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# System prompt for Second Opinion AI
SECOND_OPINION_SYSTEM_PROMPT = """You are ByOnco Second Opinion AI, a specialized medical assistant focused exclusively on oncology (cancer) care.

CRITICAL RULES:
1. You MUST ONLY answer questions related to:
   - Cancer diagnosis, treatment, and management
   - Oncology-related health concerns
   - Treatment options, side effects, and recovery
   - Nutrition and lifestyle during cancer treatment
   - Hospital and specialist recommendations for cancer care
   - Medical report interpretation (biopsy, scans, pathology)

2. You MUST NOT answer:
   - Non-medical questions (weather, sports, general knowledge)
   - Non-oncology medical questions (heart disease, diabetes, etc. unless related to cancer treatment)
   - Legal, financial, or personal advice unrelated to cancer care
   - Questions about other diseases or conditions

3. If asked a non-oncology or non-medical question, politely redirect:
   "I'm specialized in oncology (cancer) care. I can only provide information related to cancer diagnosis, treatment, and management. For a comprehensive second opinion from an actual oncologist, please consider our premium Second Opinion service where board-certified specialists review your case."

4. Always emphasize:
   - This is AI assistance, not a replacement for professional medical consultation
   - For detailed second opinions, users should use the premium service with actual oncologists
   - Encourage users to consult their treating physicians

5. Be empathetic, clear, and evidence-based in your responses.

6. When interpreting medical reports or scans, provide general guidance but always recommend consulting with an oncologist for definitive interpretation.

7. If a user asks about a specific case or wants a detailed second opinion, guide them to the premium service:
   "For a comprehensive second opinion from board-certified oncologists with 15+ years of experience, please use our premium Second Opinion service. Our specialists will review your complete case, including all medical reports, and provide a detailed analysis within 12-24 hours."

Your responses should be helpful, accurate, and always within the scope of oncology care."""


class SecondOpinionAIService:
    """Service for Second Opinion AI chat operations"""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=api_key)
    
    async def chat(self, message: str, file_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message with health/oncology restrictions
        
        Args:
            message: User's message
            file_content: Optional extracted text from uploaded medical report
        
        Returns:
            Dict with 'response' and 'usage_info'
        """
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": SECOND_OPINION_SYSTEM_PROMPT},
            ]
            
            # Add file content if provided
            user_message = message
            if file_content:
                user_message = f"""User Question: {message}

Attached Medical Report Content:
{file_content}

Please analyze the medical report and answer the user's question. If the report contains critical findings, recommend consulting with an oncologist through our premium Second Opinion service for detailed review."""
            
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI Chat Completions API with token limit
            from whatsapp.rate_limiter import MAX_TOKENS_PER_RESPONSE
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency, can upgrade to gpt-4o if needed
                messages=messages,
                temperature=0.7,
                max_tokens=MAX_TOKENS_PER_RESPONSE,  # Enforce cost control
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "usage_info": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def is_health_related(self, message: str) -> bool:
        """
        Basic check if message is health/oncology related
        This is a fallback - the system prompt should handle most cases
        """
        health_keywords = [
            'cancer', 'oncology', 'tumor', 'tumour', 'malignant', 'benign',
            'chemotherapy', 'radiation', 'surgery', 'treatment', 'diagnosis',
            'biopsy', 'pathology', 'scan', 'mri', 'ct', 'pet', 'x-ray',
            'symptom', 'pain', 'health', 'medical', 'doctor', 'physician',
            'hospital', 'clinic', 'medication', 'drug', 'therapy', 'patient',
            'disease', 'illness', 'condition', 'stage', 'metastasis'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in health_keywords)

