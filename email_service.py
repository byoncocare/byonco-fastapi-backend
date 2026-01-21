"""
Compatibility shim for email_service.py
This file maintains backward compatibility for imports from the old location.
All imports are redirected to the new location: app.core.email_service
"""
from app.core.email_service import EmailService

__all__ = ["EmailService"]
