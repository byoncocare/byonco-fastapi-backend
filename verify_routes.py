"""
Quick verification script to check if all routes are properly registered
Run this before deploying to ensure routes are accessible
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("🔍 Verifying backend routes...")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing imports...")
    from server import app
    print("   ✅ Server imports successfully")
    
    from rare_cancers.api_routes import create_api_router
    print("   ✅ Rare cancers router imports successfully")
    
    from hospitals.api_routes import create_api_router as create_hospitals_router
    print("   ✅ Hospitals router imports successfully")
    
    # List all routes
    print("\n2. Registered API routes:")
    print("-" * 60)
    api_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'N/A'
            path = route.path
            if path.startswith('/api'):
                api_routes.append((path, methods))
                print(f"   {path:40} [{methods}]")
    
    # Check for required routes
    print("\n3. Checking required routes...")
    required_routes = [
        '/api/cancer-types',
        '/api/rare-cancers',
        '/api/hospitals',
        '/api/doctors'
    ]
    
    found_routes = [r[0] for r in api_routes]
    missing_routes = []
    
    for required in required_routes:
        # Check exact match or if route starts with required path
        found = any(r == required or r.startswith(required + '/') for r in found_routes)
        if found:
            print(f"   ✅ {required}")
        else:
            print(f"   ❌ {required} - MISSING!")
            missing_routes.append(required)
    
    if missing_routes:
        print(f"\n❌ ERROR: {len(missing_routes)} required route(s) are missing!")
        print("   Please check backend/server.py for route registration.")
        sys.exit(1)
    else:
        print("\n✅ All required routes are registered!")
        print(f"\n📊 Total API routes found: {len(api_routes)}")
        print("\n✅ Backend is ready for deployment!")
        sys.exit(0)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

