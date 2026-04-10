import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

# Configuration
BASE_URL = "http://127.0.0.1:8005"
ENDPOINT = "/api/v1/orchestrate"
CONCURRENT_REQUESTS = 5 # Scaling back to 10 to ensure stability first
TOTAL_REQUESTS = 20
AUTH_TOKEN = "AUDIT_MODE_TOKEN"

def send_request(session):
    start = time.time()
    try:
        response = session.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"query": "Explain hyperscale readiness."},
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=30.0
        )
        duration = time.time() - start
        if response.status_code == 200:
            return duration
        else:
            print(f"Failed: {response.status_code}")
            return -1
    except Exception as e:
        # print(f"Error: {e}")
        return -1

def run_load_test():
    print(f"Starting Threaded Load Test: {TOTAL_REQUESTS} total, {CONCURRENT_REQUESTS} concurrent...")
    
    results = []
    start_time = time.time()
    
    with requests.Session() as session:
        # Pre-warm session or set headers
        session.headers.update({"Authorization": f"Bearer {AUTH_TOKEN}"})
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(send_request, session) for _ in range(TOTAL_REQUESTS)]
            results = [f.result() for f in futures]
            
    total_time = time.time() - start_time
    success_times = [r for r in results if r > 0]
    failures = results.count(-1)
    
    if success_times:
        print("\n--- Threaded Load Test Results ---")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests/sec: {len(success_times) / total_time:.2f}")
        print(f"Average Latency: {statistics.mean(success_times)*1000:.2f}ms")
        if len(success_times) > 1:
            print(f"P95 Latency: {statistics.quantiles(success_times, n=20)[18]*1000:.2f}ms")
        print(f"Successes: {len(success_times)}")
        print(f"Failures: {failures}")
        print("----------------------------------\n")
    else:
        print("All requests failed.")

if __name__ == "__main__":
    run_load_test()
