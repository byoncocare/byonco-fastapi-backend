"""
WhatsApp webhook and API routes
Handles Meta webhook verification and incoming messages
"""
from fastapi import APIRouter, Request, HTTPException, Header, Body, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Optional, Dict, Any
import logging

from .config import config
from .parser import parse_webhook_payload
from .store import store
from .client import send_text_message, verify_connection
from .messages import get_response_for_user_async

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    """Create WhatsApp API router"""
    router = APIRouter()
    
    @router.get("/webhook")
    async def verify_webhook(
        request: Request,
        hub_mode: Optional[str] = Query(None, alias="hub.mode"),
        hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
        hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
    ):
        """
        Meta webhook verification endpoint.
        Returns hub.challenge if verification token matches.
        No authentication required - this is called by Meta for verification.
        """
        # Log request details (never log secrets)
        logger.info(f"GET /api/whatsapp/webhook - method={request.method}, path={request.url.path}")
        logger.info(f"Webhook verification: mode={hub_mode}, token_present={bool(hub_verify_token)}, challenge_present={bool(hub_challenge)}")
        
        # If no hub.mode parameter, return 200 OK (health check)
        if not hub_mode:
            logger.info("Webhook GET called without hub.mode - returning OK (health check)")
            return PlainTextResponse("ok", status_code=200)
        
        # If hub.mode == "subscribe", enforce token verification
        if hub_mode == "subscribe":
            if hub_verify_token == config.verify_token:
                logger.info("✅ Webhook verification successful - returning challenge")
                return PlainTextResponse(hub_challenge or "", status_code=200)
            else:
                token_match = hub_verify_token == config.verify_token if hub_verify_token else False
                logger.warning(f"❌ Webhook verification failed - status=403, mode={hub_mode}, token_match={token_match}")
                return PlainTextResponse("Forbidden", status_code=403)
        
        # For any other hub.mode value, return 200 OK
        logger.info(f"Webhook GET called with hub.mode={hub_mode} (not subscribe) - returning OK")
        return PlainTextResponse("ok", status_code=200)
    
    @router.head("/webhook")
    async def verify_webhook_head(request: Request):
        """
        Meta webhook HEAD endpoint for health checks.
        Returns 200 OK with no body.
        """
        logger.info(f"HEAD /api/whatsapp/webhook - method={request.method}, path={request.url.path}")
        return PlainTextResponse("", status_code=200)
    
    @router.post("/webhook")
    async def handle_webhook(request: Request):
        """
        Handle incoming WhatsApp webhook events from Meta.
        Processes messages and sends replies.
        No authentication required - this is called by Meta.
        ALWAYS returns HTTP 200 with {"status": "ok"} to Meta.
        """
        # Log incoming request
        logger.info(f"POST /api/whatsapp/webhook - method={request.method}, path={request.url.path}")
        
        # Parse JSON payload exactly once
        try:
            payload = await request.json()
        except Exception as e:
            # JSON parsing failed - log and return OK to Meta
            logger.warning(f"Failed to parse webhook JSON: {type(e).__name__}")
            return JSONResponse({"status": "ok"})
        
        try:
            object_type = payload.get('object', 'unknown')
            logger.info(f"Received webhook payload: object={object_type}")
            
            # Parse incoming messages (tolerant - returns empty list if no messages)
            messages = parse_webhook_payload(payload)
            
            if not messages:
                # No text messages, might be status update
                logger.info("⚠️ WhatsApp webhook POST ignored (no messages)")
                return JSONResponse({"status": "ok"})
            
            logger.info(f"Parsed {len(messages)} incoming message(s)")
            
            # Process each message
            for msg in messages:
                try:
                    # Mask wa_id for logging (show first 6, mask last 4)
                    masked_wa_id = f"{msg.wa_id[:6]}****{msg.wa_id[-4:]}" if len(msg.wa_id) > 10 else "****"
                    logger.info(f"Incoming message: type={msg.message_type}, from={masked_wa_id}, message_id={msg.message_id}")
                    
                    # Idempotency check
                    if store.is_message_processed(msg.message_id):
                        logger.info(f"Message {msg.message_id} already processed, skipping")
                        continue
                    
                    # Mark as processed
                    store.mark_message_processed(msg.message_id)
                    
                    # Get user state and determine response (async with OpenAI integration)
                    response_text = await get_response_for_user_async(msg.wa_id, msg.message_body)
                    
                    # Send reply
                    try:
                        await send_text_message(msg.wa_id, response_text)
                        logger.info(f"✅ Sent reply to {masked_wa_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send reply to {masked_wa_id}: {e}", exc_info=True)
                        # Continue processing other messages even if one fails
                
                except Exception as e:
                    logger.error(f"Error processing message {msg.message_id}: {e}", exc_info=True)
                    continue
            
            # Always return 200 to Meta
            logger.info("✅ WhatsApp webhook POST processed successfully")
            return JSONResponse({"status": "ok"})
        
        except Exception as e:
            # Any other error - log and still return OK to Meta
            logger.error(f"Error handling webhook: {type(e).__name__}", exc_info=False)
            return JSONResponse({"status": "ok"})
    
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
    
    @router.get("/debug/webhook-status")
    async def webhook_status():
        """
        Safe debug endpoint to check webhook configuration.
        Returns only boolean flags - never exposes secrets.
        """
        return JSONResponse({
            "whatsapp_access_token_present": bool(config.access_token),
            "whatsapp_verify_token_present": bool(config.verify_token),
            "whatsapp_phone_number_id_present": bool(config.phone_number_id),
            "webhook_ready": bool(config.access_token and config.verify_token and config.phone_number_id)
        })
    
    return router
