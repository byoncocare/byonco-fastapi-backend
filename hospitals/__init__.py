"""
Compatibility shim for hospitals module
This module has been moved to app.api.modules.hospitals
Import everything from the new location
"""
import sys
from pathlib import Path

# Ensure app directory is in path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import from new location
from app.api.modules.hospitals import *
