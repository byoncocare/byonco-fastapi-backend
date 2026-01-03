"""
WhatsApp configuration management
Loads and validates environment variables for WhatsApp integration
"""
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def env(name: str, default: str = "") -> str:
    """Get environment variable and strip all whitespace/newlines"""
    value = os.environ.get(name, default) or ""
    return value.strip()


class WhatsAppConfig:
    """WhatsApp configuration from environment variables"""
    
    def __init__(self):
        self.verify_token = env("WHATSAPP_VERIFY_TOKEN", "praesidio_whatsapp_verify")
        self.access_token = env("WHATSAPP_ACCESS_TOKEN", "")
        self.phone_number_id = env("WHATSAPP_PHONE_NUMBER_ID", "")
        self.graph_version = env("WHATSAPP_GRAPH_VERSION", "v21.0")
        self.app_env = env("APP_ENV", "local")
        self.admin_api_key = env("ADMIN_API_KEY", "")
        self.meta_app_secret = env("META_APP_SECRET", "")
        self.debug_key = env("DEBUG_KEY", "")
        self.waba_id = env("WHATSAPP_WABA_ID", "")
        
        # Validate required fields
        if not self.access_token:
            logger.warning("⚠️ WHATSAPP_ACCESS_TOKEN not set - outbound messages will fail")
        if not self.phone_number_id:
            logger.warning("⚠️ WHATSAPP_PHONE_NUMBER_ID not set - outbound messages will fail")
        if not self.meta_app_secret:
            logger.warning("⚠️ META_APP_SECRET not set - webhook signature verification disabled")
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.app_env.lower() == "production"
    
    def is_local(self) -> bool:
        """Check if running in local environment"""
        return self.app_env.lower() == "local"
    
    def validate_admin_key(self, provided_key: Optional[str]) -> bool:
        """Validate admin API key for protected endpoints"""
        if self.is_local():
            return True  # No auth required in local
        if not self.admin_api_key:
            return True  # If not set, allow (for backward compatibility)
        return provided_key == self.admin_api_key


# Global config instance
config = WhatsAppConfig()

