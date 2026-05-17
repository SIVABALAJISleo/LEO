import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.primitive_decomposition.decomposition_engine import PrimitiveDecompositionEngine

def run_benchmark():
    print("=" * 70)
    print("  LEO RUNTIME — PHASE 1: PRIMITIVE DECOMPOSITION ENGINE")
    print("=" * 70)
    
    engine = PrimitiveDecompositionEngine()
    
    # 5 Test Enterprise Queries representing different workload styles
    test_queries = [
        "Audit the procurement contract to extract liability clauses and compare key terms.",
        "Verify compliance for the new HR policy and check for data protection regulation gaps.",
        "Reconcile the Q3 financial invoice statement against the ledger.",
        "Alert the risk team and escalate the account balance warning.",
        "Draft an open-ended narrative poem about the beauty of the cosmos." # High Ambiguity/Gap test
    ]
    
    total_queries = len(test_queries)
    gaps_found = 0
    total_ambiguity = 0.0
    coverage_sum = 0.0
    
    for i, q in enumerate(test_queries):
        print(f"\n[{i+1}/{total_queries}] Query: '{q}'")
        res = engine.decompose(q)
        
        print(f"  Decomposition Pipeline:")
        if res["primitive_gap"]:
            print("    [!] SEMANTIC GAP DETECTED: No stable primitives match this open workload.")
            gaps_found += 1
        else:
            for step in res["pipeline"]:
                print(f"    Step {step['step']}: {step['primitive']} (Layer {step['layer']}) -> {step['description']}")
                
        print(f"  Ambiguity Rate: {res['ambiguity_rate']:.2f}")
        print(f"  Coverage Score: {res['coverage_score']:.2f}")
        
        total_ambiguity += res["ambiguity_rate"]
        coverage_sum += res["coverage_score"]
        
    print("\n" + "=" * 70)
    print("  PHASE 1 DECOMPOSITION REPORT SUMMARY")
    print("=" * 70)
    print(f"  Total Queries Tested : {total_queries}")
    print(f"  Primitive Gaps Found  : {gaps_found} ({(gaps_found/total_queries)*100:.1f}%)")
    print(f"  Average Ambiguity Rate: {total_ambiguity/total_queries:.2f}")
    print(f"  Average Coverage Score: {coverage_sum/total_queries:.2f}")
    
    print("\nLEO cleanly intercepts open-ended prompts (like general writing tasks) and")
    print("reconstructs them into a strict graph of domain stable operators to govern compute.")

if __name__ == "__main__":
    run_benchmark()
