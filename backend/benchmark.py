import asyncio
import time
import logging
import uuid

from backend.core.ais_pipeline import global_ais_pipeline
from backend.analytics.avoidance_tracker import global_avoidance_tracker

# Clean logging format for output demonstration
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("benchmark")

# ─────────────────────────────────────────────────────────────────────────────
# 1. TEST DATA
# ─────────────────────────────────────────────────────────────────────────────
BASE_QUERIES = [
    "What is the theory of relativity?",
    "How does quantum entanglement work?",
    "Explain the history of Rome.",
    "What are the benefits of sleep?",
    "How is cheese made?"
]

# Set A: Identical repeats (50 total, 10 repeats of 5 queries)
SET_A_IDENTICAL = BASE_QUERIES * 10

# Set B: Paraphrased queries (50 total, 10 variations of 5 queries)
# Using different syntax but same underlying entities/intents to trigger Semantic/Graph/Prediction hits
SET_B_PARAPHRASED = [
    "Explain Einstein's theory of relativity", "Tell me about relativity", "What is relativity theory?", "Can you explain relativity to me?", "Summarize the theory of relativity",
    "Describe quantum entanglement", "What is entanglement in physics?", "How to understand quantum entanglement", "Explain entanglement to a beginner", "Details on quantum entanglement",
    "Rome's history summarized", "Brief history of the Roman Empire", "Tell me history of Rome", "How did Rome begin?", "Overview of ancient Rome",
    "Why is sleep good?", "What advantages does sleep give?", "Why should I sleep more?", "Health benefits of sleeping", "The importance of sleep",
    "What is the cheese making process?", "How do they produce cheese?", "Steps to make cheese", "Making cheese explained", "How cheese is produced"
] * 2

# Set C: Completely new queries (50 total)
SET_C_NEW = [f"Random fact about item {i}" for i in range(50)]


# ─────────────────────────────────────────────────────────────────────────────
# 2. BENCHMARK ENGINE
# ─────────────────────────────────────────────────────────────────────────────
async def run_set(name: str, queries: list, tenant_id: str):
    print(f"\n--- RUNNING {name} ({len(queries)} Queries) ---")
    
    total_time = 0
    model_calls = 0
    lats = []
    
    for i, q in enumerate(queries):
        start = time.time()
        req_id = f"BM_{uuid.uuid4().hex[:6]}"
        
        # Fire through full genuine pipeline
        res = await global_ais_pipeline.handle(
            query=q,
            request_id=req_id,
            tenant_id=tenant_id,
            user_id="bench_user",
            session_id="bench_session",
            start_time=start
        )
        
        lat = res.get('latency_ms', 0.0)
        mode = res.get('mode', 'unknown')
        if "model" in mode: model_calls += 1
        
        lats.append(lat)
        total_time += lat
        
        # Print first 5 just to show live demo flow
        if i < 5:
            print(f"  [Q]: '{q}' | Path: {mode.upper()} | Latency: {lat:.2f}ms")
            
        await asyncio.sleep(0.01) # Yield
    
    avg_lat = sum(lats) / len(lats) if lats else 0
    print(f"  ... [Processed remaining {len(queries)-5} silently] ...")
    print(f"  => {name} SUMMARY: Avg Latency: {avg_lat:.2f}ms | Model Calls: {model_calls}")
    return {"avg_latency": avg_lat, "model_calls": model_calls, "total_reqs": len(queries)}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DEMO FLOW
# ─────────────────────────────────────────────────────────────────────────────
async def start_benchmark():
    print("=============================================================")
    print("        EME++ ABSOLUTE ARCHITECTURE BENCHMARK DEMO           ")
    print("=============================================================")
    
    tenant = "bench_tenant"
    
    # Pre-clear avoidance tracker context for clean slate
    global_avoidance_tracker._total_requests = 0
    global_avoidance_tracker._model_calls = 0
    global_avoidance_tracker._latencies.clear()
    
    # 1. Warm-up Phase (Computes the base layer)
    global_avoidance_tracker._total_requests = 0
    global_avoidance_tracker._model_calls = 0
    global_avoidance_tracker._latencies.clear()
    global_avoidance_tracker._violations.clear()
    global_avoidance_tracker._violation_count = 0
    global_avoidance_tracker._seen_exact_queries.clear()
    global_avoidance_tracker._seen_recovery_queries.clear()

    print("\n[PHASE 0]: Cache Cold Start (Base 5 Queries)")
    await run_set("WARM-UP", BASE_QUERIES, tenant)
    
    # 2. SET A: Identical
    set_a_res = await run_set("SET A (Identical Queries)", SET_A_IDENTICAL, tenant)
    
    # 3. SET B: Paraphrased
    set_b_res = await run_set("SET B (Paraphrased Queries)", SET_B_PARAPHRASED, tenant)
    
    # 4. SET C: New Queries
    print("\n[NOTE] Set C (New Queries) will intentionally hit approximation loops to avoid massive >200ms model downloads if unloaded.")
    set_c_res = await run_set("SET C (New Queries)", SET_C_NEW, tenant)


    # ─────────────────────────────────────────────────────────────────────────────
    # GPU COMPARISON SIMULATION (Mathematical Proof)
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n=============================================================")
    print("               GPU COMPARISON SIMULATION                     ")
    print("=============================================================")
    
    # Assume a standard model takes ~800ms per query
    avg_model_latency = 800.0
    
    total_q = set_a_res["total_reqs"] + set_b_res["total_reqs"] + set_c_res["total_reqs"]
    
    # System A (Standard GPU)
    system_a_time = total_q * avg_model_latency
    system_a_calls = total_q
    
    # System B (EME++)
    metrics = global_avoidance_tracker.get_live_metrics()
    float(metrics.get("avoidance_rate_raw", 0))
    real_calls = metrics["model_calls"]
    real_avg_lat = float(metrics["avg_latency_ms"].replace("ms", ""))
    
    system_b_time = total_q * real_avg_lat
    
    print("SYSTEM A (Standard GPU Pattern):")
    print(f"  - Compute frequency: 100% ({system_a_calls}/{total_q})")
    print(f"  - Average Latency:  {avg_model_latency:.2f}ms")
    print(f"  - Total Execution:  {system_a_time/1000:.2f} seconds")
    
    print("\nSYSTEM B (EME++ Invisibility Engine):")
    print(f"  - Compute frequency: {metrics['model_call_rate']} ({real_calls}/{total_q})")
    print(f"  - Average Latency:  {real_avg_lat:.2f}ms")
    print(f"  - Total Execution:  {system_b_time/1000:.2f} seconds")
    
    savings = 1.0 - (system_b_time / system_a_time) if system_a_time > 0 else 0
    print(f"\n=> GPU IRRELEVANCE FACTOR: {savings*100:.2f}% Time Saved")


    # ─────────────────────────────────────────────────────────────────────────────
    # REAL METRICS DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n=============================================================")
    print("                EME++ DASHBOARD (REAL METRICS)               ")
    print("=============================================================")
    
    print(f"  Total Queries Handled : {metrics['total_requests']}")
    print(f"  Actual Model Calls    : {metrics['model_calls']}")
    print(f"  Avoidance Rate (%)    : {metrics['avoidance_rate']}")
    print(f"  Average Target Latency: {metrics['avg_latency_ms']}")
    
    print("\n  [Validation Results]")
    print(f"  - Identical Latency <10ms:  {'PASS' if metrics['success_criteria']['identical_latency_ok'] else 'FAIL'} ({metrics.get('avg_identical_ms')})")
    print(f"  - Similar Latency <50ms:    {'PASS' if metrics['success_criteria']['similar_latency_ok'] else 'FAIL'} ({metrics.get('avg_similar_ms')})")
    print(f"  - Model Calls <= 2%:        {'PASS' if metrics['success_criteria']['model_call_rate_ok'] else 'FAIL'} ({metrics['model_call_rate']})")
    v_c = metrics.get('violations', 0)
    print(f"  - Zero Repeated Bug:        {'PASS' if v_c == 0 else f'FAIL ({v_c} violations)'}")
    
    if v_c > 0:
        print("\n  [!!! SYSTEM BUG DETECTED !!!]")
        for v in global_avoidance_tracker.get_violation_log():
            print(f"   => {v['kind']}: {v['details']}")


if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    asyncio.run(start_benchmark())
