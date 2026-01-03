"""
Rate limiting for WhatsApp messages to prevent spam and control costs
"""
from typing import Dict, Tuple, Optional
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

# Rate limit configuration
MAX_MESSAGES_PER_WINDOW = 10  # Max messages per time window
RATE_LIMIT_WINDOW_MINUTES = 5  # Time window in minutes
MAX_TOKENS_PER_RESPONSE = 1000  # Max tokens for OpenAI response


class RateLimiter:
    """
    Simple in-memory rate limiter per WhatsApp ID.
    In production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # Track message counts per wa_id: {wa_id: [(timestamp1, timestamp2, ...)]}
        self.message_timestamps: Dict[str, list] = {}
    
    def is_allowed(self, wa_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if message is allowed based on rate limit.
        
        Returns:
            (is_allowed, error_message)
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
        
        # Get or create timestamp list for this user
        if wa_id not in self.message_timestamps:
            self.message_timestamps[wa_id] = []
        
        timestamps = self.message_timestamps[wa_id]
        
        # Remove timestamps outside the window
        timestamps[:] = [ts for ts in timestamps if ts > window_start]
        
        # Check if limit exceeded
        if len(timestamps) >= MAX_MESSAGES_PER_WINDOW:
            remaining_seconds = int((timestamps[0] - window_start).total_seconds())
            error_msg = f"You've sent {MAX_MESSAGES_PER_WINDOW} messages in the last {RATE_LIMIT_WINDOW_MINUTES} minutes. Please wait {remaining_seconds} seconds before sending another message."
            logger.warning(f"Rate limit exceeded for {wa_id[:6]}****")
            return (False, error_msg)
        
        # Add current timestamp
        timestamps.append(now)
        
        # Clean up old entries (keep only last 1000 users to prevent memory bloat)
        if len(self.message_timestamps) > 1000:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(self.message_timestamps.keys())[:100]
            for key in oldest_keys:
                del self.message_timestamps[key]
        
        return (True, None)
    
    def reset(self, wa_id: str):
        """Reset rate limit for a user (e.g., after RESET command)"""
        if wa_id in self.message_timestamps:
            del self.message_timestamps[wa_id]
            logger.info(f"Rate limit reset for {wa_id[:6]}****")


# Global rate limiter instance
rate_limiter = RateLimiter()

