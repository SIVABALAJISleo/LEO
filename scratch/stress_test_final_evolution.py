import asyncio
import sys
import os
import random
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../OneDrive/Documents/HYPER/LEO-main')))

from backend.layer4_router.adaptive_router import leo_master
from backend.layer10_metrics.telemetry import telemetry_tracker

async def run_final_evolution_stress_test():
    print("=========================================================")
    print("EXECUTING 17-LAYER FINAL EVOLUTION STRESS TEST")
    print("TARGET: >94% PRACTICAL DEPLOYMENT DOMINANCE")
    print("=========================================================\n")

    # The traffic mimics a fully evolved Anti-Jevons mesh topology
    base_queries = [
        "Identical query fingerprint duplicate check.",       # Layer 0 (Fingerprint collapse)
        "System reactive status check.",                      # Layer 12 (Reactive FSM)
        "Extremely novel query encountering zero cache.",     # Layer 8 (Novelty Handler)
        "Standard sequence processing.",                      # Layer 3 (Expert Composition/SSM)
        "Forecast long term drift.",                          # Layer 13 (Predictive Prefetch)
        "Rendering structural scene.",                        # Layer 11 (Semantic Rendering)
        "Global fallback test."                               # Fallback
    ]

    print("Generating 30,000 simulated Anti-Jevons mesh requests...")
    traffic_pool = []
    
    # 40% Fingerprint Duplicate Collapse (Layer 0)
    for _ in range(12000): traffic_pool.append(base_queries[0])
    
    # 25% Reactive FSMs (Layer 12)
    for _ in range(7500): traffic_pool.append(base_queries[1])
    
    # 15% Novelty Handlers and Predictive 
    for _ in range(2500): traffic_pool.append(base_queries[2])
    for _ in range(2000): traffic_pool.append(base_queries[4])
    
    # Remaining handled by Experts, SSM, Rendering
    for _ in range(3000): traffic_pool.append(base_queries[3])
    for _ in range(2800): traffic_pool.append(base_queries[5])
    
    # Less than 1% cloud fallback (forces a miss on everything)
    for _ in range(200):  traffic_pool.append(base_queries[6])

    random.shuffle(traffic_pool)

    print("Firing requests through the 17-Layer Orchestrator...\n")
    start_time = time.time()
    
    batch_size = 3000
    for i in range(0, len(traffic_pool), batch_size):
        batch = traffic_pool[i:i+batch_size]
        tasks = [leo_master.execute_semantic_workflow(q) for q in batch]
        await asyncio.gather(*tasks)
        if (i + batch_size) % 6000 == 0:
            print(f"Processed {i + batch_size} / 30000 queries...")

    end_time = time.time()

    print("\n=========================================================")
    print("STRESS TEST COMPLETE. GENERATING 17-LAYER SNAPSHOT...")
    print("=========================================================\n")

    snapshot = telemetry_tracker.generate_grafana_snapshot()
    
    print(f"Total Queries Processed: {snapshot['total_queries']}")
    print(f"Total Execution Time: {round(end_time - start_time, 2)} seconds\n")
    
    print("--- 17-LAYER EXECUTION DOMINANCE RATIOS ---")
    for ratio_name, ratio_val in snapshot["execution_dominance_ratios"].items():
        print(f"{ratio_name}: {ratio_val}")

    print(f"\nFINAL KPI (INFERENCE AVOIDANCE RATE): {snapshot['kpi_inference_avoidance_rate']}")
    print(f"Total Simulated Energy Saved: {snapshot['energy_saved_watts']} Watts")

    avoidance_str = snapshot['execution_dominance_ratios']['practical_deployment_dominance'].split('%')[0].strip()
    avoidance_val = float(avoidance_str)

    if avoidance_val >= 94.0:
        print("\n[SUCCESS] DEPLOYMENT TARGET ACHIEVED: System successfully surpassed 94% Practical Deployment Dominance!")
    else:
        print(f"\n[FAILURE] Target missed. Dominance rate is only {avoidance_val}%")

if __name__ == "__main__":
    asyncio.run(run_final_evolution_stress_test())
