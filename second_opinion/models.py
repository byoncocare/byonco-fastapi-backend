"""
Pydantic models for Second Opinion AI
"""
from pydantic import BaseModel, Field
from typing import Optional


class SecondOpinionChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message/question")
    file_content: Optional[str] = Field(None, description="Extracted text content from uploaded medical report")


class SecondOpinionChatResponse(BaseModel):
    """Response model for AI chat"""
    response: str = Field(..., description="AI's response")
    usage_info: dict = Field(..., description="Token usage information")

