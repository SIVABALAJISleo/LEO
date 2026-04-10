import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_telemetry():
    print("Testing CPU Telemetry Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/api/v1/compute/telemetry")
        if res.status_code == 200:
            print("Telemetry SUCCESS:", json.dumps(res.json(), indent=2))
        else:
            print("Telemetry FAILED:", res.text)
    except Exception as e:
        print("Telemetry Connection ERROR:", e)

def test_benchmark():
    print("\nTesting CPU LLM Inference Benchmark Endpoint...")
    payload = {
        "prompt": "What is CPU inference and why is it useful?",
        "max_tokens": 50
    }
    try:
        # Give it a longer timeout as it's doing blocking inference
        start = time.time()
        res = requests.post(f"{BASE_URL}/api/v1/compute/benchmark", json=payload, timeout=120)
        end = time.time()
        
        if res.status_code == 200:
            print(f"Benchmark SUCCESS (Took {end-start:.2f}s):", json.dumps(res.json(), indent=2))
        else:
            print("Benchmark FAILED:", res.text)
    except Exception as e:
        print("Benchmark ERROR:", e)

if __name__ == "__main__":
    print("--- Starting CPU-First Verification ---")
    test_telemetry()
    test_benchmark()
    print("--- Verification Complete ---")
