import requests

BASE_URL = "http://127.0.0.1:8005"
TOKEN = "mock_token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_health():
    print("Testing /health...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_orchestrate():
    print("\nTesting /api/orchestrate...")
    payload = {"query": "Hello HYPER"}
    try:
        r = requests.post(f"{BASE_URL}/api/orchestrate", headers=HEADERS, json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json().get('status')}")
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_rag_query():
    print("\nTesting /api/rag/query...")
    payload = {"query": "Tell me about SDGP"}
    try:
        r = requests.post(f"{BASE_URL}/api/rag/query", headers=HEADERS, json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: Object returned successfully (length: {len(str(r.json()))})")
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_status():
    print("\nTesting /status...")
    try:
        r = requests.get(f"{BASE_URL}/status", headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response Metrics: {r.json().get('metrics', 'No metrics found')}")
        else:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()
    test_orchestrate()
    test_rag_query()
    test_status()
