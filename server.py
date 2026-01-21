"""
Compatibility shim for server.py
This file maintains backward compatibility for the old entry point.
The actual FastAPI app is now in app.main:app
"""
# Import the app from the new location
from app.main import app
from app.database import db, client

# Re-export for backward compatibility
__all__ = ["app", "db", "client"]
