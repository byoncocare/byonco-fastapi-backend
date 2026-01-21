"""
Seed data for Hospitals API
Imports from the main seed_data module
"""
# Import from the new location (data_seed.py shim also works for backward compatibility)
from app.data.seed_data import HOSPITALS, DOCTORS, ALL_CANCERS, CITIES

# Export for use in other modules
__all__ = ['HOSPITALS', 'DOCTORS', 'ALL_CANCERS', 'CITIES']



















