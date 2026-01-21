# Compatibility shim for get_started
# This module has been moved to app.api.modules.get_started
# Import everything from the new location
from app.api.modules.get_started import *

__all__ = ['*']
