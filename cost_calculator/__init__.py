# Compatibility shim for cost_calculator
# This module has been moved to app.api.modules.cost_calculator
# Import everything from the new location
from app.api.modules.cost_calculator import *

__all__ = ['*']
