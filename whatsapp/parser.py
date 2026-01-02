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
        message_type: str = "text"
    ):
        self.wa_id = wa_id
        self.message_id = message_id
        self.timestamp = timestamp
        self.message_body = message_body
        self.message_type = message_type
    
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
                        # Only process text messages
                        msg_type = msg.get("type", "")
                        if msg_type != "text":
                            logger.debug(f"Ignoring non-text message type: {msg_type}")
                            continue
                        
                        wa_id = msg.get("from")
                        if not wa_id:
                            logger.debug("Message missing 'from' field")
                            continue
                        
                        message_id = msg.get("id")
                        if not message_id:
                            logger.debug("Message missing 'id' field")
                            continue
                        
                        timestamp = msg.get("timestamp", "")
                        
                        # Extract text message
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
                        
                    except Exception as e:
                        logger.debug(f"Error parsing individual message: {type(e).__name__}")
                        continue
        
    except Exception as e:
        logger.debug(f"Error parsing webhook payload: {type(e).__name__}")
    
    return messages

