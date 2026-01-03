"""
WhatsApp Business Cloud API client
Handles outbound message sending via Meta Graph API with retry/backoff
"""
import httpx
from typing import Optional, Dict, Any
import logging
import asyncio
import random
from .config import config

logger = logging.getLogger(__name__)


async def send_text_message_with_retry(
    to: str,
    text: str,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Send a text message via WhatsApp Business Cloud API with retry/backoff.
    
    Retries on: 429 (rate limit), 500, 502, 503, 504
    Does NOT retry on: 400, 401, 403 (client errors)
    
    Args:
        to: WhatsApp ID of recipient (e.g., "919876543210")
        text: Message text to send (will be trimmed if too long)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
    
    Returns:
        Dict with API response or error details
    
    Raises:
        ValueError: If required config is missing
        httpx.HTTPError: If API request fails after all retries
    """
    if not config.access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN not configured")
    if not config.phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID not configured")
    
    # Trim message if too long (WhatsApp limit is 4096 characters)
    if len(text) > 4096:
        text = text[:4090] + "..."
        logger.warning(f"Message trimmed to 4096 chars for {to[:6]}****")
    
    if not text.strip():
        raise ValueError("Message text cannot be empty")
    
    url = f"https://graph.facebook.com/{config.graph_version}/{config.phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {config.access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                # Success
                if response.status_code < 400:
                    result = response.json()
                    message_id = result.get("messages", [{}])[0].get("id", "unknown")
                    logger.info(f"✅ Sent WhatsApp message to {to[:6]}**** (msg_id={message_id[:20]}...)")
                    return {
                        "success": True,
                        "message_id": message_id,
                        "response": result
                    }
                
                # Client errors - do NOT retry
                if response.status_code in [400, 401, 403]:
                    error_detail = "Unknown error"
                    try:
                        error_response = response.json()
                        error_detail = error_response.get("error", {}).get("message", str(response.status_code))
                    except:
                        error_detail = f"HTTP {response.status_code}"
                    
                    logger.error(f"❌ Client error sending WhatsApp message to {to[:6]}****: {error_detail}")
                    raise httpx.HTTPStatusError(
                        f"WhatsApp API client error: {error_detail}",
                        request=response.request,
                        response=response
                    )
                
                # Server errors or rate limit - retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = initial_delay * (2 ** attempt) + random.uniform(0, 0.5)
                        logger.warning(
                            f"⚠️ Retry {attempt + 1}/{max_retries} for {to[:6]}**** "
                            f"(status={response.status_code}, delay={delay:.2f}s)"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Last attempt failed
                        error_detail = f"HTTP {response.status_code}"
                        try:
                            error_response = response.json()
                            error_detail = error_response.get("error", {}).get("message", error_detail)
                        except:
                            pass
                        
                        logger.error(f"❌ Failed after {max_retries} retries: {error_detail}")
                        raise httpx.HTTPStatusError(
                            f"WhatsApp API error after retries: {error_detail}",
                            request=response.request,
                            response=response
                        )
                
                # Other status codes - don't retry
                response.raise_for_status()
        
        except httpx.RequestError as e:
            # Network errors - retry
            if attempt < max_retries:
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 0.5)
                logger.warning(f"⚠️ Network error, retry {attempt + 1}/{max_retries} (delay={delay:.2f}s)")
                await asyncio.sleep(delay)
                last_exception = e
                continue
            else:
                logger.error(f"❌ Network error after {max_retries} retries: {e}")
                raise
        
        except httpx.HTTPStatusError as e:
            # Re-raise client errors and final server errors
            raise
    
    # Should not reach here, but handle it
    if last_exception:
        raise last_exception
    raise httpx.HTTPError("Failed to send message after retries")


async def send_text_message(to: str, text: str) -> Dict[str, Any]:
    """
    Send a text message via WhatsApp Business Cloud API (with retry/backoff).
    Wrapper around send_text_message_with_retry for backward compatibility.
    """
    return await send_text_message_with_retry(to, text)


async def verify_connection() -> Dict[str, Any]:
    """
    Verify WhatsApp API connection by making a lightweight request.
    Does not send a message, just checks if credentials are valid.
    
    Returns:
        Dict with verification status
    """
    if not config.access_token or not config.phone_number_id:
        return {
            "ready": False,
            "error": "Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID"
        }
    
    # Try to get phone number info (lightweight request)
    url = f"https://graph.facebook.com/{config.graph_version}/{config.phone_number_id}"
    headers = {
        "Authorization": f"Bearer {config.access_token}"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params={"fields": "id"})
            response.raise_for_status()
            return {
                "ready": True,
                "phone_number_id": config.phone_number_id,
                "graph_version": config.graph_version
            }
    except Exception as e:
        logger.warning(f"WhatsApp API verification failed: {e}")
        return {
            "ready": False,
            "error": str(e)
        }

