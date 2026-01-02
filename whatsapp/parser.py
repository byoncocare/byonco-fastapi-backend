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
        
        if payload.get("object") != "whatsapp_business_account":
            logger.debug(f"Ignoring non-WhatsApp webhook: {payload.get('object')}")
            return messages
        
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                
                # Skip status updates (delivery receipts, read receipts)
                if "statuses" in value:
                    logger.debug("Ignoring status update webhook")
                    continue
                
                # Extract messages
                message_list = value.get("messages", [])
                contacts = value.get("contacts", [])
                
                # Create contact lookup
                contact_map = {}
                for contact in contacts:
                    wa_id = contact.get("wa_id")
                    if wa_id:
                        contact_map[wa_id] = contact
                
                # Parse each message
                for msg in message_list:
                    try:
                        wa_id = msg.get("from")
                        if not wa_id:
                            logger.warning("Message missing 'from' field")
                            continue
                        
                        message_id = msg.get("id")
                        if not message_id:
                            logger.warning("Message missing 'id' field")
                            continue
                        
                        timestamp = msg.get("timestamp", "")
                        
                        # Extract text message
                        text_obj = msg.get("text")
                        if text_obj:
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
                        
                        # TODO: Handle interactive replies (button clicks, list selections)
                        # interactive = msg.get("interactive")
                        # if interactive:
                        #     # Handle button/list selections
                        #     pass
                        
                    except Exception as e:
                        logger.error(f"Error parsing individual message: {e}", exc_info=True)
                        continue
        
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {e}", exc_info=True)
    
    return messages

