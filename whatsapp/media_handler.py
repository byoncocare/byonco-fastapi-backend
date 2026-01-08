"""
WhatsApp media handler
Downloads media files (images, PDFs) from Meta Graph API
"""
import httpx
from typing import Optional, Tuple
import logging
from .config import config

logger = logging.getLogger(__name__)

# Max file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PDF_SIZE = 20 * 1024 * 1024  # 20 MB


async def download_media(media_id: str) -> Tuple[Optional[bytes], Optional[str], Optional[int]]:
    """
    Download media file from Meta Graph API.
    
    Args:
        media_id: Media ID from WhatsApp message
        
    Returns:
        Tuple of (file_bytes, mime_type, file_size) or (None, None, None) on error
    """
    if not config.access_token:
        logger.error("WHATSAPP_ACCESS_TOKEN not configured")
        return None, None, None
    
    try:
        # Step 1: Get media URL from Meta Graph API
        url = f"https://graph.facebook.com/{config.graph_version}/{media_id}"
        headers = {
            "Authorization": f"Bearer {config.access_token}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get media metadata
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            media_info = response.json()
            
            media_url = media_info.get("url")
            mime_type = media_info.get("mime_type", "")
            
            if not media_url:
                logger.error(f"No URL in media info for media_id={media_id[:20]}...")
                return None, None, None
            
            # Step 2: Download the actual file
            download_response = await client.get(
                media_url,
                headers={"Authorization": f"Bearer {config.access_token}"},
                timeout=60.0  # Longer timeout for large files
            )
            download_response.raise_for_status()
            
            file_bytes = download_response.content
            file_size = len(file_bytes)
            
            # Validate file size
            if mime_type.startswith("image/"):
                if file_size > MAX_IMAGE_SIZE:
                    logger.warning(f"Image too large: {file_size} bytes (max {MAX_IMAGE_SIZE})")
                    return None, None, None
            elif mime_type == "application/pdf":
                if file_size > MAX_PDF_SIZE:
                    logger.warning(f"PDF too large: {file_size} bytes (max {MAX_PDF_SIZE})")
                    return None, None, None
            
            logger.info(f"Downloaded media: media_id={media_id[:20]}..., size={file_size} bytes, mime_type={mime_type}")
            return file_bytes, mime_type, file_size
            
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("error", {}).get("message", str(e))
        except:
            error_detail = str(e)
        
        logger.error(f"Failed to download media {media_id[:20]}...: {error_detail}")
        return None, None, None
    
    except httpx.RequestError as e:
        logger.error(f"Network error downloading media: {e}")
        return None, None, None
    
    except Exception as e:
        logger.error(f"Unexpected error downloading media: {e}", exc_info=True)
        return None, None, None
