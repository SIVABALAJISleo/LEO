import asyncio
import time
from collections import Counter
from backend.core.orchestrator import hyper_engine
from backend.predictive.answer_store import global_predictive_store

async def simulate_user(user_id, num_requests=10):
    modes = []
    tenant_id = "stress_tenant"
    
    # Pre-populate for some hits
    global_predictive_store.save_answer("Frequent Query", "Frequent Answer", 0.99, tenant_id=tenant_id)

    for i in range(num_requests):
        query = "Frequent Query" if i % 2 == 0 else f"Unique Query {user_id}_{i}"
        result = await hyper_engine.process(query, f"req_{user_id}_{i}", tenant_id=tenant_id)
        modes.append(result["mode"])
        await asyncio.sleep(0.01) # Short delay
    return modes

async def run_stress_test(num_users=50):
    print(f"Starting Stress Test with {num_users} concurrent users...")
    start = time.time()
    
    tasks = [simulate_user(i) for i in range(num_users)]
    results = await asyncio.gather(*tasks)
    
    flat_results = [m for sublist in results for m in sublist]
    counts = Counter(flat_results)
    
    duration = time.time() - start
    print(f"\nStress Test Complete in {duration:.2f}s")
    print("Hit Distribution:")
    for mode, count in counts.items():
        print(f"  {mode}: {count} ({count/len(flat_results)*100:.1f}%)")

if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    asyncio.run(run_stress_test())
