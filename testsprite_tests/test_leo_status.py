# test_leo_status.py
# TestSprite backend test for LEO system status and metrics endpoints.

import os
import requests

def test_leo_status_endpoint():
    target_url = globals().get("TARGET_URL", "http://localhost:8005")
    url = f"{target_url}/api/v1/leo/status"
    
    headers = globals().get("__AUTH_HEADERS__", {})
    
    print(f"Sending GET request to {url}...")
    response = requests.get(url, headers=headers, timeout=15)
    
    assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}. Body: {response.text}"
    
    data = response.json()
    # Check that core status fields exist
    assert "status" in data or "semantic_store_size" in data, f"Missing status indicators: {data}"
    
    print("LEO Status Endpoint check PASSED ✓")

# Execute the test function
test_leo_status_endpoint()
