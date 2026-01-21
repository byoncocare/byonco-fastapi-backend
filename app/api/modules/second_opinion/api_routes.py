"""
API routes for Second Opinion AI
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging
import io
import PyPDF2

from .models import SecondOpinionChatRequest, SecondOpinionChatResponse
from .service import SecondOpinionAIService

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def create_api_router():
    """
    Create and return the API router for Second Opinion AI.
    """
    router = APIRouter(prefix="/api/second-opinion-ai", tags=["second-opinion-ai"])
    
    try:
        ai_service = SecondOpinionAIService()
    except ValueError as e:
        logger.error(f"Failed to initialize Second Opinion AI service: {e}")
        ai_service = None
    
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"[PDF file - text extraction failed: {str(e)}]"
    
    @router.post("/chat", response_model=SecondOpinionChatResponse)
    async def chat(
        request: SecondOpinionChatRequest,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ):
        """
        Process a chat message with health/oncology restrictions
        
        - Validates that the message is health/oncology related
        - Returns AI response with usage information
        - Requires authentication (optional for now, can be enforced later)
        """
        if not ai_service:
            raise HTTPException(
                status_code=503,
                detail="Second Opinion AI service is not available. Please check OPENAI_API_KEY configuration."
            )
        
        try:
            # Basic validation - check if message seems health-related
            if not ai_service.is_health_related(request.message):
                logger.warning(f"Non-health related query detected: {request.message[:100]}")
                # Still process it - the system prompt will handle the restriction
            
            result = await ai_service.chat(
                message=request.message,
                file_content=request.file_content
            )
            
            return SecondOpinionChatResponse(
                response=result["response"],
                usage_info=result["usage_info"]
            )
            
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process chat request: {str(e)}"
            )
    
    @router.post("/upload-files")
    async def upload_files(
        files: List[UploadFile] = File(...),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ):
        """
        Upload and extract text from medical reports (PDF, DOC, images)
        Returns extracted text content for AI analysis
        """
        extracted_texts = []
        
        for file in files:
            try:
                content = await file.read()
                
                # Handle PDF files
                if file.content_type == "application/pdf":
                    text = extract_text_from_pdf(content)
                    extracted_texts.append(f"[{file.filename}]\n{text}")
                
                # For other file types (DOC, images), return placeholder
                # In production, integrate OCR services for images and DOC parsers
                else:
                    extracted_texts.append(f"[{file.filename} - Content extraction for {file.content_type} files requires additional processing]")
                    
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                extracted_texts.append(f"[{file.filename} - Error: {str(e)}]")
        
        return {
            "extracted_text": "\n\n".join(extracted_texts),
            "file_count": len(files)
        }
    
    return router

