"""
Meta webhook signature verification
Verifies X-Hub-Signature-256 header using META_APP_SECRET
"""
import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def verify_webhook_signature(
    raw_body: bytes,
    signature_header: Optional[str],
    app_secret: str
) -> bool:
    """
    Verify Meta webhook signature using HMAC SHA256.
    
    Args:
        raw_body: Raw request body bytes (exactly as received)
        signature_header: X-Hub-Signature-256 header value (format: "sha256=<hex>")
        app_secret: META_APP_SECRET from environment
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not app_secret:
        logger.warning("META_APP_SECRET not configured - signature verification skipped")
        return True  # Allow if not configured (backward compatibility)
    
    if not signature_header:
        logger.warning("X-Hub-Signature-256 header missing")
        return False
    
    # Parse signature header: "sha256=<hex>"
    if not signature_header.startswith("sha256="):
        logger.warning(f"Invalid signature header format: {signature_header[:20]}...")
        return False
    
    try:
        received_signature = signature_header[7:]  # Remove "sha256=" prefix
        
        # Compute expected signature
        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(received_signature, expected_signature)
        
        if not is_valid:
            logger.warning("Webhook signature verification failed")
        
        return is_valid
    
    except Exception as e:
        logger.error(f"Error verifying signature: {type(e).__name__}", exc_info=False)
        return False

