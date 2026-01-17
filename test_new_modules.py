"""
Test script to verify the new modular backend structure
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    
    # Test hospitals module
    print("\n1. Testing hospitals module...")
    from hospitals.api_routes import create_api_router as create_hospitals_router
    hospitals_router = create_hospitals_router()
    print("   ✅ Hospitals router created successfully")
    print(f"   Routes: {[r.path for r in hospitals_router.routes]}")
    
    # Test rare_cancers module
    print("\n2. Testing rare_cancers module...")
    from rare_cancers.api_routes import create_api_router as create_rare_cancers_router
    rare_cancers_router = create_rare_cancers_router()
    print("   ✅ Rare cancers router created successfully")
    print(f"   Routes: {[r.path for r in rare_cancers_router.routes]}")
    
    # Test server import
    print("\n3. Testing server import...")
    from server import app
    print("   ✅ Server imports successfully")
    
    # List all routes
    print("\n4. Available API routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"   {route.path} [{methods}]")
    
    print("\n✅ All tests passed! Backend structure is working correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



















