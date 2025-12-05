"""Quick test script to verify server routes"""
import asyncio
from server import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_routes():
    print("Testing server routes...\n")
    
    # Test root route
    print("1. Testing root route (/)...")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test API root
    print("2. Testing API root (/api/)...")
    response = client.get("/api/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test hospitals
    print("3. Testing hospitals endpoint (/api/hospitals)...")
    response = client.get("/api/hospitals")
    print(f"   Status: {response.status_code}")
    hospitals = response.json()
    print(f"   Hospitals returned: {len(hospitals) if isinstance(hospitals, list) else 'Error'}")
    if isinstance(hospitals, list) and len(hospitals) > 0:
        print(f"   First hospital: {hospitals[0].get('name', 'N/A')}\n")
    else:
        print(f"   Response: {hospitals}\n")
    
    # Test cancer types
    print("4. Testing cancer types endpoint (/api/cancer-types)...")
    response = client.get("/api/cancer-types")
    print(f"   Status: {response.status_code}")
    cancer_types = response.json()
    print(f"   Cancer types returned: {len(cancer_types) if isinstance(cancer_types, list) else 'Error'}")
    if isinstance(cancer_types, list) and len(cancer_types) > 0:
        print(f"   First cancer type: {cancer_types[0].get('name', 'N/A')}\n")
    else:
        print(f"   Response: {cancer_types}\n")
    
    # Test cities
    print("5. Testing cities endpoint (/api/cities)...")
    response = client.get("/api/cities")
    print(f"   Status: {response.status_code}")
    cities = response.json()
    print(f"   Response: {cities}\n")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    test_routes()



