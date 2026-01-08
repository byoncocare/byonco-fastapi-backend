"""
WhatsApp webhook payload parser
Safely extracts incoming messages from Meta webhook payloads
"""
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IncomingMessage:
    """Parsed incoming WhatsApp message"""
    
    def __init__(
        self,
        wa_id: str,
        message_id: str,
        timestamp: str,
        message_body: str,
        message_type: str = "text",
        media_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        caption: Optional[str] = None
    ):
        self.wa_id = wa_id
        self.message_id = message_id
        self.timestamp = timestamp
        self.message_body = message_body
        self.message_type = message_type  # "text", "image", "document", "video"
        self.media_id = media_id  # For image/document/video
        self.mime_type = mime_type  # e.g., "image/jpeg", "application/pdf"
        self.caption = caption  # Optional caption for media messages
    
    def __repr__(self):
        return f"IncomingMessage(wa_id={self.wa_id}, message_id={self.message_id}, type={self.message_type})"


def parse_webhook_payload(payload: Dict[str, Any]) -> List[IncomingMessage]:
    """
    Parse Meta webhook payload and extract incoming text messages.
    Returns list of IncomingMessage objects.
    Ignores status updates (delivery receipts, read receipts, etc.)
    Tolerant: returns empty list if payload structure is unexpected.
    """
    messages = []
    
    try:
        # Meta webhook structure:
        # {
        #   "object": "whatsapp_business_account",
        #   "entry": [
        #     {
        #       "id": "...",
        #       "changes": [
        #         {
        #           "value": {
        #             "messaging_product": "whatsapp",
        #             "metadata": {...},
        #             "contacts": [...],
        #             "messages": [...]
        #           }
        #         }
        #       ]
        #     }
        #   ]
        # }
        
        if not isinstance(payload, dict):
            logger.debug("Payload is not a dictionary")
            return messages
        
        if payload.get("object") != "whatsapp_business_account":
            logger.debug(f"Ignoring non-WhatsApp webhook: {payload.get('object')}")
            return messages
        
        entries = payload.get("entry", [])
        if not entries:
            logger.debug("No entries in webhook payload")
            return messages
        
        if not isinstance(entries, list):
            logger.debug("Entries is not a list")
            return messages
        
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            
            changes = entry.get("changes", [])
            if not isinstance(changes, list):
                continue
            
            for change in changes:
                if not isinstance(change, dict):
                    continue
                
                value = change.get("value", {})
                if not isinstance(value, dict):
                    continue
                
                # Skip status updates (delivery receipts, read receipts)
                if "statuses" in value:
                    logger.debug("Ignoring status update webhook")
                    continue
                
                # Extract messages - tolerant if missing
                message_list = value.get("messages", [])
                if not message_list:
                    # No messages in this change - this is normal for some webhook types
                    continue
                
                if not isinstance(message_list, list):
                    continue
                
                contacts = value.get("contacts", [])
                if not isinstance(contacts, list):
                    contacts = []
                
                # Parse each message
                for msg in message_list:
                    if not isinstance(msg, dict):
                        continue
                    
                    try:
                        msg_type = msg.get("type", "")
                        wa_id = msg.get("from")
                        if not wa_id:
                            logger.debug("Message missing 'from' field")
                            continue
                        
                        message_id = msg.get("id")
                        if not message_id:
                            logger.debug("Message missing 'id' field")
                            continue
                        
                        timestamp = msg.get("timestamp", "")
                        
                        # Handle text messages
                        if msg_type == "text":
                            text_obj = msg.get("text")
                            if not text_obj or not isinstance(text_obj, dict):
                                continue
                            
                            message_body = text_obj.get("body", "").strip()
                            if message_body:
                                messages.append(IncomingMessage(
                                    wa_id=wa_id,
                                    message_id=message_id,
                                    timestamp=timestamp,
                                    message_body=message_body,
                                    message_type="text"
                                ))
                                logger.info(f"Parsed text message from {wa_id}: {message_body[:50]}")
                        
                        # Handle image messages
                        elif msg_type == "image":
                            image_obj = msg.get("image")
                            if not image_obj or not isinstance(image_obj, dict):
                                continue
                            
                            media_id = image_obj.get("id")
                            mime_type = image_obj.get("mime_type", "image/jpeg")
                            caption = msg.get("caption", "").strip() if msg.get("caption") else None
                            
                            if media_id:
                                messages.append(IncomingMessage(
                                    wa_id=wa_id,
                                    message_id=message_id,
                                    timestamp=timestamp,
                                    message_body=caption or "[Image attachment]",
                                    message_type="image",
                                    media_id=media_id,
                                    mime_type=mime_type,
                                    caption=caption
                                ))
                                logger.info(f"Parsed image message from {wa_id}, media_id={media_id[:20]}...")
                        
                        # Handle document messages (PDFs)
                        elif msg_type == "document":
                            doc_obj = msg.get("document")
                            if not doc_obj or not isinstance(doc_obj, dict):
                                continue
                            
                            media_id = doc_obj.get("id")
                            mime_type = doc_obj.get("mime_type", "application/pdf")
                            filename = doc_obj.get("filename", "document.pdf")
                            caption = msg.get("caption", "").strip() if msg.get("caption") else None
                            
                            # Only process PDFs
                            if media_id and mime_type == "application/pdf":
                                messages.append(IncomingMessage(
                                    wa_id=wa_id,
                                    message_id=message_id,
                                    timestamp=timestamp,
                                    message_body=caption or f"[PDF attachment: {filename}]",
                                    message_type="document",
                                    media_id=media_id,
                                    mime_type=mime_type,
                                    caption=caption
                                ))
                                logger.info(f"Parsed PDF document from {wa_id}, media_id={media_id[:20]}..., filename={filename}")
                            else:
                                logger.debug(f"Ignoring non-PDF document: {mime_type}")
                        
                        # Handle video messages (polite rejection)
                        elif msg_type == "video":
                            video_obj = msg.get("video")
                            if not video_obj or not isinstance(video_obj, dict):
                                continue
                            
                            caption = msg.get("caption", "").strip() if msg.get("caption") else None
                            # Create a text message response instead of processing video
                            messages.append(IncomingMessage(
                                wa_id=wa_id,
                                message_id=message_id,
                                timestamp=timestamp,
                                message_body="[VIDEO_REJECTION]",
                                message_type="video",
                                caption=caption
                            ))
                            logger.info(f"Parsed video message from {wa_id} (will be rejected)")
                        
                        else:
                            logger.debug(f"Ignoring unsupported message type: {msg_type}")
                        
                    except Exception as e:
                        logger.debug(f"Error parsing individual message: {type(e).__name__}")
                        continue
        
    except Exception as e:
        logger.debug(f"Error parsing webhook payload: {type(e).__name__}")
    
    return messages

