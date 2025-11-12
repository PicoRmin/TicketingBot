"""
Test script for CORS and API connectivity
"""
import sys
from pathlib import Path

# Add the project root to the sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.config import settings


def test_cors():
    """Test CORS configuration"""
    print("=" * 60)
    print("🧪 Testing CORS Configuration")
    print("=" * 60)
    
    # Check CORS origins
    print(f"\n📋 CORS Origins from config:")
    origins = settings.cors_origins_list
    for origin in origins:
        print(f"  ✅ {origin}")
    
    # Test API connectivity
    print(f"\n🌐 Testing API connectivity...")
    base_url = settings.API_BASE_URL
    
    try:
        with httpx.Client(timeout=5.0) as client:
            # Test health endpoint
            print(f"\n1️⃣ Testing health endpoint...")
            response = client.get(f"{base_url}/health")
            if response.status_code == 200:
                print(f"   ✅ Health check: {response.json()}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
            
            # Test CORS headers
            print(f"\n2️⃣ Testing CORS headers...")
            response = client.get(
                f"{base_url}/health",
                headers={"Origin": "http://localhost:5173"}
            )
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-credentials": response.headers.get("access-control-allow-credentials"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
            }
            
            print(f"   CORS Headers:")
            for key, value in cors_headers.items():
                if value:
                    print(f"     ✅ {key}: {value}")
                else:
                    print(f"     ⚠️  {key}: Not found")
            
            # Test OPTIONS request (preflight)
            print(f"\n3️⃣ Testing OPTIONS (preflight) request...")
            response = client.options(
                f"{base_url}/health",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in (200, 204):
                print(f"   ✅ Preflight request successful")
            else:
                print(f"   ❌ Preflight request failed")
                
    except httpx.ConnectError:
        print(f"   ❌ Cannot connect to {base_url}")
        print(f"   💡 Make sure Backend is running:")
        print(f"      uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed")
    print("=" * 60)


if __name__ == "__main__":
    test_cors()

