# WhatsApp Attachment Support Implementation

## Overview
Extended WhatsApp webhook to support image and PDF attachments while maintaining existing text message functionality.

## Features Implemented

### 1. Message Type Support
- **Text messages**: Existing functionality preserved
- **Image messages**: Download, OCR extraction, and AI analysis
- **PDF documents**: Text extraction + OCR fallback for scanned PDFs
- **Video messages**: Polite rejection message

### 2. Media Processing Flow

```
User sends attachment
    ↓
Webhook receives message (parser.py)
    ↓
Download media from Meta Graph API (media_handler.py)
    ↓
Extract text (extractor.py)
    - Images: OCR with multilingual support
    - PDFs: Text extraction → OCR fallback if needed
    ↓
Pass extracted text to oncology AI service (messages.py)
    ↓
Generate response with:
    - Report summary
    - Flagged values
    - Recommended questions for oncologist
    - Next-step guidance
```

### 3. Multilingual Support
- OCR supports: English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada
- Uses Tesseract with multiple language packs
- Handles mixed-language documents

### 4. Error Handling
- File size limits: 10MB for images, 20MB for PDFs
- Page limits: Max 10 pages for PDFs
- Graceful fallback if OCR dependencies unavailable
- User-friendly error messages

### 5. Logging
- Message type, media size, extraction method
- Success/failure status
- Pages processed (for PDFs)
- Extracted text length

## Files Modified/Created

### New Files
- `backend/whatsapp/media_handler.py`: Downloads media from Meta Graph API
- `backend/whatsapp/extractor.py`: Text extraction (OCR + PDF parsing)

### Modified Files
- `backend/whatsapp/parser.py`: Extended to parse image/document/video messages
- `backend/whatsapp/api_routes.py`: Webhook handler processes attachments
- `backend/whatsapp/messages.py`: Added `process_attachment_async()` function
- `requirements.txt`: Added dependencies
- `backend/requirements.txt`: Added dependencies

## Dependencies Added

```txt
pdfplumber==0.11.4      # PDF text extraction
pytesseract==0.3.13     # OCR wrapper
pdf2image==1.17.0       # PDF to image conversion for OCR
```

**Note**: Pillow is already present in requirements.

## System Requirements

### Tesseract OCR Installation

The system requires Tesseract OCR to be installed on the server:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-tam tesseract-ocr-tel tesseract-ocr-ben tesseract-ocr-guj tesseract-ocr-kan
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Tesseract OCR
3. Add to PATH or set `TESSDATA_PREFIX` environment variable
4. Download language packs for Hindi, Marathi, etc.

**poppler (for PDF to image conversion):**

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download from: https://github.com/oschwartz10612/poppler-windows/releases

## Usage Limits

- File attachments count against daily limit: `MAX_FILE_ATTACHMENTS_PER_DAY = 1`
- Text prompts: `MAX_TEXT_PROMPTS_PER_DAY = 2`
- Limits reset daily

## API Integration

### Meta Graph API Endpoints Used

1. **Get Media URL**: `GET /{media-id}`
   - Returns media URL and metadata
   - Requires Bearer token authentication

2. **Download Media**: `GET {media_url}`
   - Downloads actual file bytes
   - Requires Bearer token authentication

## Error Messages

### User-Facing Messages
- **Video rejection**: "I can only process text messages, images, and PDF documents..."
- **Download failure**: "I couldn't download your file. Please try uploading again..."
- **Extraction failure**: "I couldn't read the text from your file. Please make sure..."
- **Limit exceeded**: Uses existing `LIMIT_EXCEEDED_FILE` message

## Testing Recommendations

1. **Test image uploads**:
   - Clear, well-lit medical report images
   - Blurry/low-quality images (should fail gracefully)
   - Images with mixed languages

2. **Test PDF uploads**:
   - PDFs with embedded text
   - Scanned PDFs (OCR fallback)
   - Large PDFs (>10 pages, should limit processing)
   - Corrupted PDFs (should fail gracefully)

3. **Test limits**:
   - Daily file attachment limit
   - File size limits
   - Page limits for PDFs

4. **Test error handling**:
   - Network failures during download
   - Missing Tesseract installation
   - Invalid media IDs

## Configuration

No additional environment variables required. Uses existing:
- `WHATSAPP_ACCESS_TOKEN`: For Meta Graph API authentication
- `WHATSAPP_PHONE_NUMBER_ID`: For API calls
- `WHATSAPP_GRAPH_VERSION`: API version (default: v21.0)

## Notes

- Existing text message flow is completely unchanged
- Attachment processing only occurs for onboarded users
- Extracted text is passed to the same oncology AI service used for text queries
- All logging follows existing patterns (privacy-conscious, no PII)
