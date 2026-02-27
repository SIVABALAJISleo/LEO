import requests
import json
import uuid
import time
import os

BASE_URL = "http://127.0.0.1:8005"
USERNAME = f"test_user_{uuid.uuid4().hex[:8]}"
PASSWORD = "SecurePassword123!"
EMAIL = f"{USERNAME}@hyper-test.local"

def run_test_suite():
    print(f"--- Starting HYPER End-to-End Integration Suite ---")
    
    # 1. Test Registration
    print(f"\n[1] Registering User: {USERNAME}")
    try:
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": USERNAME,
            "password": PASSWORD,
            "email": EMAIL
        })
        print(f"Status: {reg_res.status_code}")
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    except Exception as e:
        print(f"Error during registration: {e}")
        return

    # 2. Test Login
    print(f"\n[2] Logging in...")
    access_token = ""
    try:
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD,
            "email": EMAIL
        })
        print(f"Status: {login_res.status_code}")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        access_token = login_res.json().get("access_token")
        print(f"Received Token: {access_token[:10]}...")
    except Exception as e:
        print(f"Error during login: {e}")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Test Orchestration with Token
    print(f"\n[3] Testing Authenticated Orchestration...")
    try:
        orch_res = requests.post(f"{BASE_URL}/api/orchestrate", headers=headers, json={
            "query": "Synthesize a 3D model of a cyber-city."
        })
        print(f"Status: {orch_res.status_code}")
        if orch_res.status_code == 200:
            print(f"Expert Used: {orch_res.json().get('expert')}")
            print(f"Result: {orch_res.json().get('result')[:100]}...")
        else:
             print(f"Response: {orch_res.text}")
    except Exception as e:
        print(f"Error during orchestration: {e}")
        
    # 4. Agentic Auto-Healer Crash Test
    print(f"\n[4] Intentionally Triggering Agentic Healer (Zero Division Simulation)")
    try:
        # We hit the /debug/direct endpoint but pass a payload we know isn't handled gracefully natively
        # Actually, let's just trigger a chaotic condition if we can, or we can use the RAG endpoint with weird data
        # To guarantee a crash, we'll request a URL that deliberately raises an Exception (we will add a /crash endpoint for testing)
        crash_res = requests.get(f"{BASE_URL}/trigger-error-for-agentic-test", headers=headers)
        print(f"Status: {crash_res.status_code}")
        
        data = crash_res.json()
        if data.get("agentic_intervention"):
            print(f"SUCCESS: Agentic AI intervened!")
            print(f"AI Resolution: {data.get('healer_action')}")
            print(f"AI Result: {data.get('result')}")
        else:
            print(f"FAILED: The system crashed natively or returned an unexpected response.")
            print(crash_res.text)
    except Exception as e:
        print(f"Error triggering crash: {e}")

if __name__ == "__main__":
    run_test_suite()
