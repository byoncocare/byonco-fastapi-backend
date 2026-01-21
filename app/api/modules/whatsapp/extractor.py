"""
Text extraction from images and PDFs
Supports OCR for images and scanned PDFs, text extraction for PDFs with embedded text
Multilingual support for Indian languages (Hindi, Marathi, etc.)
"""
import io
import logging
from typing import Optional, Tuple
from PIL import Image
import pdfplumber

logger = logging.getLogger(__name__)

# Try importing OCR dependencies (may not be available in all environments)
convert_from_bytes = None
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.warning("pdf2image not available - OCR fallback for scanned PDFs will be disabled")

pytesseract = None
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - OCR will be disabled")

# Max pages to process for PDFs (to prevent excessive processing)
MAX_PDF_PAGES = 10

# Tesseract language codes for multilingual OCR
# Supports: English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada
TESSERACT_LANGS = "eng+hin+mar+tam+tel+ben+guj+kan"


def extract_text_from_image(image_bytes: bytes, mime_type: str) -> Tuple[Optional[str], bool]:
    """
    Extract text from image using OCR.
    
    Args:
        image_bytes: Image file bytes
        mime_type: MIME type of the image
        
    Returns:
        Tuple of (extracted_text, success)
    """
    if not TESSERACT_AVAILABLE:
        logger.error("pytesseract not available - cannot perform OCR on images")
        return None, False
    
    try:
        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Perform OCR with multilingual support
        # Using multiple languages helps with mixed-language documents
        extracted_text = pytesseract.image_to_string(
            image,
            lang=TESSERACT_LANGS,
            config='--psm 6'  # Assume uniform block of text
        )
        
        extracted_text = extracted_text.strip()
        
        if not extracted_text or len(extracted_text) < 10:
            logger.warning("OCR extracted very little or no text from image")
            return None, False
        
        logger.info(f"OCR extracted {len(extracted_text)} characters from image")
        return extracted_text, True
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}", exc_info=True)
        return None, False


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[Optional[str], bool, int]:
    """
    Extract text from PDF.
    First tries text extraction, then falls back to OCR if no text found.
    
    Args:
        pdf_bytes: PDF file bytes
        
    Returns:
        Tuple of (extracted_text, success, pages_processed)
    """
    try:
        # Step 1: Try text extraction first (for PDFs with embedded text)
        extracted_text = ""
        pages_processed = 0
        
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(total_pages, MAX_PDF_PAGES)
                
                logger.info(f"PDF has {total_pages} pages, processing first {pages_to_process}")
                
                for i, page in enumerate(pdf.pages[:pages_to_process]):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                        pages_processed += 1
                
                # Check if we got meaningful text
                extracted_text = extracted_text.strip()
                
                if extracted_text and len(extracted_text) > 50:
                    logger.info(f"Extracted {len(extracted_text)} characters from PDF using text extraction ({pages_processed} pages)")
                    return extracted_text, True, pages_processed
                
                logger.info("PDF has no embedded text, falling back to OCR")
                
        except Exception as e:
            logger.warning(f"Text extraction failed, trying OCR: {e}")
        
        # Step 2: OCR fallback (for scanned PDFs)
        if not PDF2IMAGE_AVAILABLE or not TESSERACT_AVAILABLE or convert_from_bytes is None or pytesseract is None:
            logger.warning("OCR dependencies not available - cannot perform OCR fallback for scanned PDFs")
            return None, False, pages_processed
        
        try:
            # Convert PDF pages to images
            images = convert_from_bytes(
                pdf_bytes,
                dpi=300,  # Higher DPI for better OCR accuracy
                first_page=1,
                last_page=min(MAX_PDF_PAGES, None)  # Limit pages
            )
            
            extracted_text = ""
            pages_processed = 0
            
            for i, image in enumerate(images):
                # Convert to RGB if necessary
                if image.mode != "RGB":
                    image = image.convert("RGB")
                
                # Perform OCR
                page_text = pytesseract.image_to_string(
                    image,
                    lang=TESSERACT_LANGS,
                    config='--psm 6'
                )
                
                if page_text.strip():
                    extracted_text += f"\n--- Page {i+1} ---\n{page_text.strip()}\n"
                    pages_processed += 1
            
            extracted_text = extracted_text.strip()
            
            if not extracted_text or len(extracted_text) < 50:
                logger.warning("OCR extracted very little or no text from PDF")
                return None, False, pages_processed
            
            logger.info(f"Extracted {len(extracted_text)} characters from PDF using OCR ({pages_processed} pages)")
            return extracted_text, True, pages_processed
            
        except Exception as e:
            logger.error(f"OCR fallback failed: {e}", exc_info=True)
            return None, False, pages_processed
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
        return None, False, 0


def extract_text_from_media(file_bytes: bytes, mime_type: str) -> Tuple[Optional[str], bool, dict]:
    """
    Extract text from media file (image or PDF).
    
    Args:
        file_bytes: File bytes
        mime_type: MIME type of the file
        
    Returns:
        Tuple of (extracted_text, success, metadata)
        metadata includes: pages_processed (for PDFs), extraction_method
    """
    metadata = {
        "extraction_method": None,
        "pages_processed": 0
    }
    
    if mime_type.startswith("image/"):
        text, success = extract_text_from_image(file_bytes, mime_type)
        if success:
            metadata["extraction_method"] = "OCR"
        return text, success, metadata
    
    elif mime_type == "application/pdf":
        text, success, pages = extract_text_from_pdf(file_bytes)
        metadata["pages_processed"] = pages
        if success:
            metadata["extraction_method"] = "text_extraction_or_OCR"
        return text, success, metadata
    
    else:
        logger.warning(f"Unsupported MIME type for extraction: {mime_type}")
        return None, False, metadata
