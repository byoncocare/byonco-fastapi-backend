from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

print("Testing Backend Endpoints...")
print("=" * 50)

for path in ['/api/cancer-types', '/api/rare-cancers']:
    print(f"\nPATH: {path}")
    try:
        response = client.get(path)
        print(f"STATUS: {response.status_code}")
        data = response.json()
        
        if isinstance(data, list):
            print(f"RESPONSE TYPE: List with {len(data)} items")
            if len(data) > 0:
                print(f"FIRST ITEM: {data[0]}")
        elif isinstance(data, dict):
            print(f"RESPONSE TYPE: Dictionary")
            print(f"KEYS: {list(data.keys())}")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  {key}: List with {len(value)} items")
                    if len(value) > 0:
                        print(f"    First item: {value[0]}")
                else:
                    print(f"  {key}: {type(value).__name__}")
        else:
            print(f"RESPONSE TYPE: {type(data).__name__}")
            print(f"RESPONSE: {str(data)[:400]}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("-" * 50)

