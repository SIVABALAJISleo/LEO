import asyncio
import httpx
import time
import statistics

# Configuration
BASE_URL = "http://127.0.0.1:8005"
ENDPOINT = "/api/v1/orchestrate"
CONCURRENT_REQUESTS = 100 # Can scale to 1000
TOTAL_REQUESTS = 500
AUTH_TOKEN = "AUDIT_MODE_TOKEN" # Dev bypass

async def send_request(client: httpx.AsyncClient) -> float:
    start = time.time()
    try:
        response = await client.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"query": "What is hyperscale readiness for Project HYPER?"},
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=30.0
        )
        duration = time.time() - start
        if response.status_code == 200:
            return duration
        else:
            print(f"Request failed: {response.status_code}")
            return -1
    except Exception as e:
        print(f"Error: {e}")
        return -1

async def run_load_test():
    print(f"Starting Load Test: {TOTAL_REQUESTS} total requests, {CONCURRENT_REQUESTS} concurrency...")
    
    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        
        async def sem_request():
            async with semaphore:
                return await send_request(client)
        
        start_time = time.time()
        results = await asyncio.gather(*(sem_request() for _ in range(TOTAL_REQUESTS)))
        total_time = time.time() - start_time
        
        success_times = [r for r in results if r > 0]
        failures = results.count(-1)
        
        if success_times:
            print("\n--- Load Test Results ---")
            print(f"Total Time: {total_time:.2f}s")
            print(f"Requests/sec: {len(success_times) / total_time:.2f}")
            print(f"Average Latency: {statistics.mean(success_times)*1000:.2f}ms")
            print(f"P95 Latency: {statistics.quantiles(success_times, n=20)[18]*1000:.2f}ms")
            print(f"Successes: {len(success_times)}")
            print(f"Failures: {failures}")
            print("-------------------------\n")
        else:
            print("All requests failed.")

if __name__ == "__main__":
    asyncio.run(run_load_test())
