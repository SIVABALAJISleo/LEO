import asyncio
import aiohttp
import time
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

API_URL = "http://localhost:8000/api/v1/jobs/create"
API_KEY = "sk_live_load_test_bypass" # Mock key used for bypass testing

async def spawn_job(session: aiohttp.ClientSession, job_id: int, stats: dict):
    payload = {
        "job_type": "llm",
        "parameters": {
            "prompt": f"Load Testing ID {job_id}. What is the capital of France?",
            "max_tokens": 50
        }
    }
    headers = {
         "Authorization": f"Bearer {API_KEY}",
         "Content-Type": "application/json"
    }

    start = time.time()
    try:
        async with session.post(API_URL, json=payload, headers=headers) as resp:
            latency = time.time() - start
            stats['total_latency'] += latency
            
            if resp.status == 200:
                stats['success'] += 1
            elif resp.status == 429:
                stats['rate_limited'] += 1
            elif resp.status == 402:
                stats['quota_exceeded'] += 1
            else:
                stats['errors'] += 1
                
    except Exception as e:
        stats['errors'] += 1

async def run_load_test(concurrency: int, total_jobs: int):
    print(f"{Fore.CYAN}🚀 Initiating Project HYPER Distributed Load Test")
    print(f"Targeting: {API_URL}")
    print(f"Total Jobs: {total_jobs} | Concurrency: {concurrency}{Style.RESET_ALL}\n")
    
    stats = {
        'success': 0,
        'rate_limited': 0, 
        'quota_exceeded': 0,
        'errors': 0,
        'total_latency': 0
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_spawn(job_id):
            async with semaphore:
                await spawn_job(session, job_id, stats)
                
        tasks = [bounded_spawn(i) for i in range(total_jobs)]
        await asyncio.gather(*tasks)
        
    duration = time.time() - start_time
    throughput = total_jobs / duration
    avg_latency = (stats['total_latency'] / total_jobs) * 1000 if total_jobs > 0 else 0
    
    print(f"{Fore.GREEN}=== Load Test Complete ===")
    print(f"Duration: {duration:.2f}s")
    print(f"Throughput: {throughput:.2f} req/sec")
    print(f"Avg API Latency: {avg_latency:.2f}ms")
    print(f"Success (Sent to Celery): {stats['success']}")
    print(f"{Fore.YELLOW}Redis Rate Limited (429): {stats['rate_limited']}")
    print(f"{Fore.MAGENTA}Redis Quota Reached (402): {stats['quota_exceeded']}")
    print(f"{Fore.RED}Gateway Errors (5xx): {stats['errors']}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed Pipeline Stress Test")
    parser.add_argument("-c", "--concurrency", type=int, default=100)
    parser.add_argument("-n", "--requests", type=int, default=1000)
    args = parser.parse_args()
    
    asyncio.run(run_load_test(args.concurrency, args.requests))
