"""
WhatsApp Business Cloud API client
Handles outbound message sending via Meta Graph API
"""
import httpx
from typing import Optional, Dict, Any
import logging
from .config import config

logger = logging.getLogger(__name__)


async def send_text_message(to: str, text: str) -> Dict[str, Any]:
    """
    Send a text message via WhatsApp Business Cloud API.
    
    Args:
        to: WhatsApp ID of recipient (e.g., "919876543210")
        text: Message text to send
    
    Returns:
        Dict with API response or error details
    
    Raises:
        ValueError: If required config is missing
        httpx.HTTPError: If API request fails
    """
    if not config.access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN not configured")
    if not config.phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID not configured")
    
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
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Sent WhatsApp message to {to}: {text[:50]}")
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
    
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_response = e.response.json()
            error_detail = error_response.get("error", {}).get("message", str(e))
        except:
            error_detail = str(e)
        
        logger.error(f"Failed to send WhatsApp message to {to}: {error_detail}")
        raise httpx.HTTPError(f"WhatsApp API error: {error_detail}") from e
    
    except httpx.RequestError as e:
        logger.error(f"Network error sending WhatsApp message: {e}")
        raise


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

