#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test to verify all imports work after refactoring"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    from app.main import app
    print("[OK] App imports successfully")
    print(f"[OK] App title: {app.title}")
    
    # Count routes
    routes = [r for r in app.routes if hasattr(r, "path")]
    print(f"[OK] Routes registered: {len(routes)}")
    
    # Test compatibility shim
    from server import app as app_shim
    print("[OK] Compatibility shim (server.py) works")
    
    # Test data_seed shim
    from data_seed import HOSPITALS, CITIES
    print(f"[OK] data_seed shim works (found {len(CITIES)} cities)")
    
    # Test email_service shim
    from email_service import EmailService
    print("[OK] email_service shim works")
    
    print("\n[SUCCESS] All imports successful! Refactoring is complete.")
    
except Exception as e:
    print(f"[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
