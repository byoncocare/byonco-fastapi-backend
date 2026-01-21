# Compatibility shim for payments
# This module has been moved to app.api.modules.payments
# Import everything from the new location
from app.api.modules.payments import *

__all__ = ['*']
