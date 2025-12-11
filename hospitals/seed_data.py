"""
Seed data for Hospitals API
Imports from the main data_seed.py file
"""
import sys
from pathlib import Path

# Add parent directory to path to import from data_seed
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from data_seed import HOSPITALS, DOCTORS, ALL_CANCERS, CITIES

# Export for use in other modules
__all__ = ['HOSPITALS', 'DOCTORS', 'ALL_CANCERS', 'CITIES']









