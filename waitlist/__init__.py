# Compatibility shim for waitlist
# This module has been moved to app.api.modules.waitlist
# Import everything from the new location
from app.api.modules.waitlist import *

__all__ = ['*']
