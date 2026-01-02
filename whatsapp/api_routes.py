"""
WhatsApp webhook and API routes
Handles Meta webhook verification and incoming messages
"""
from fastapi import APIRouter, Request, HTTPException, Header, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional, Dict, Any
import logging

from .config import config
from .parser import parse_webhook_payload
from .store import store
from .client import send_text_message, verify_connection
from .messages import get_response_for_user

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    """Create WhatsApp API router"""
    router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])
    
    @router.get("/webhook")
    async def verify_webhook(
        hub_mode: Optional[str] = None,
        hub_verify_token: Optional[str] = None,
        hub_challenge: Optional[str] = None
    ):
        """
        Meta webhook verification endpoint.
        Returns hub.challenge if verification token matches.
        """
        logger.info(f"Webhook verification request: mode={hub_mode}, token_present={bool(hub_verify_token)}")
        
        if hub_mode == "subscribe" and hub_verify_token == config.verify_token:
            logger.info("✅ Webhook verification successful")
            return PlainTextResponse(hub_challenge or "")
        else:
            logger.warning(f"❌ Webhook verification failed: mode={hub_mode}, token_match={hub_verify_token == config.verify_token}")
            return PlainTextResponse("Forbidden", status_code=403)
    
    @router.post("/webhook")
    async def handle_webhook(request: Request):
        """
        Handle incoming WhatsApp webhook events from Meta.
        Processes messages and sends replies.
        """
        try:
            payload = await request.json()
            logger.info(f"Received webhook payload: {payload.get('object', 'unknown')}")
            
            # Parse incoming messages
            messages = parse_webhook_payload(payload)
            
            # Process each message
            for msg in messages:
                try:
                    # Idempotency check
                    if store.is_message_processed(msg.message_id):
                        logger.info(f"Message {msg.message_id} already processed, skipping")
                        continue
                    
                    # Mark as processed
                    store.mark_message_processed(msg.message_id)
                    
                    # Get user state and determine response
                    response_text = get_response_for_user(msg.wa_id, msg.message_body)
                    
                    # Send reply
                    try:
                        await send_text_message(msg.wa_id, response_text)
                        logger.info(f"Sent reply to {msg.wa_id}")
                    except Exception as e:
                        logger.error(f"Failed to send reply to {msg.wa_id}: {e}", exc_info=True)
                        # Continue processing other messages even if one fails
                
                except Exception as e:
                    logger.error(f"Error processing message {msg.message_id}: {e}", exc_info=True)
                    continue
            
            # Always return 200 to Meta
            return JSONResponse({"status": "ok"})
        
        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            # Still return 200 to prevent Meta from retrying
            return JSONResponse({"status": "error", "message": str(e)}, status_code=200)
    
    @router.post("/send")
    async def send_message(
        to: str = Body(..., description="WhatsApp ID of recipient"),
        text: str = Body(..., description="Message text to send"),
        x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
    ):
        """
        Internal admin endpoint to send WhatsApp messages.
        Protected by ADMIN_API_KEY header in non-local environments.
        """
        # Validate admin key
        if not config.validate_admin_key(x_admin_key):
            raise HTTPException(status_code=403, detail="Invalid or missing admin API key")
        
        try:
            result = await send_text_message(to, text)
            return JSONResponse({
                "success": True,
                "message_id": result.get("message_id"),
                "to": to
            })
        except Exception as e:
            logger.error(f"Failed to send message via admin endpoint: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/debug/selftest")
    async def selftest():
        """
        Debug endpoint to check WhatsApp configuration and API connectivity.
        Does not expose sensitive tokens.
        """
        verification = await verify_connection()
        
        return JSONResponse({
            "whatsapp_configured": bool(config.access_token and config.phone_number_id),
            "verify_token_set": bool(config.verify_token),
            "phone_number_id_set": bool(config.phone_number_id),
            "graph_version": config.graph_version,
            "app_env": config.app_env,
            "api_ready": verification.get("ready", False),
            "api_error": verification.get("error") if not verification.get("ready") else None
        })
    
    return router

