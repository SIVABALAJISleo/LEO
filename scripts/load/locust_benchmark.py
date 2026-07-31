import time
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000"

function_targets = [
    "/api/v1/leo/metrics",
    "/api/v1/systems/memory/summary",
]

def make_request(path):
    start = time.time()
    try:
        res = requests.get(f"{BASE_URL}{path}", timeout=5)
        duration = (time.time() - start) * 1000
        return res.status_code, duration
    except Exception as e:
        return 500, 0

def run_concurrency_test(users=100):
    print(f"[LOAD TEST] Simulating {users} concurrent virtual users...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=users) as executor:
        futures = [executor.submit(make_request, "/api/v1/leo/metrics") for _ in range(users)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    successes = [r for r in results if r[0] == 200]
    avg_latency = sum(r[1] for r in successes) / max(len(successes), 1)
    print(f"[LOAD TEST RESULT] Total: {len(results)} | Success: {len(successes)} | Avg Latency: {avg_latency:.2f}ms")
    return len(successes), avg_latency

if __name__ == "__main__":
    run_concurrency_test(100)
