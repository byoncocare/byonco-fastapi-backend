"""
Compatibility shim for data_seed.py
This file maintains backward compatibility for imports from the old location.
All imports are redirected to the new location: app.data.seed_data
"""
# Import everything from the new location
from app.data.seed_data import (
    CITIES,
    RARE_CANCERS,
    COMMON_CANCERS,
    ALL_CANCERS,
    HOSPITALS,
    DOCTORS,
)

# Re-export for backward compatibility
__all__ = [
    "CITIES",
    "RARE_CANCERS",
    "COMMON_CANCERS",
    "ALL_CANCERS",
    "HOSPITALS",
    "DOCTORS",
]
