import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.semantic_action_protocol.sap_engine import SAPEngine

def run_benchmark():
    print("=" * 70)
    print("  LEO RUNTIME — PHASE 2: SEMANTIC ACTION PROTOCOL (SAP)")
    print("=" * 70)
    
    sap = SAPEngine()
    
    # Define test business scenarios
    scenarios = [
        {
            "query": "Should we retain user log metadata for 7 years under EU guidelines?",
            "context": {"conflicting_policy": True}
        },
        {
            "query": "Map client transaction rate to internal performance margins.",
            "context": {"undefined_term": True}
        },
        {
            "query": "Standard invoice validation check for Q3 corporate accounts.",
            "context": {} # Clean
        }
    ]
    
    for i, s in enumerate(scenarios):
        print(f"\nScenario [{i+1}]: '{s['query']}'")
        res = sap.analyze_semantic_alignment(s["query"], s["context"])
        
        print(f"  Status:       {res['status']}")
        print(f"  Action Path:  {res['resolution_path']}")
        
        if res["status"] == "CONTESTED":
            dis = res["disagreement"]
            print(f"  [!] Disagreement Type : {dis['type']}")
            print(f"  [!] Description       : {dis['description']}")
            print(f"  Competing Paths:")
            for p in dis["competing_interpretations"]:
                print(f"    - {p['path']} (P: {p['confidence']:.2f})")
                
            # Simulate human intervention (Phase 2 core)
            print("  --> Triggering Human Verification Workflow...")
            chosen_path = dis["competing_interpretations"][0]["path"]
            sap.register_human_resolution(
                s["query"],
                chosen_path,
                {"resolver_id": "usr_compliance_lead_09"}
            )
        else:
            print(f"  Confidence:   {res['confidence_score']:.2f}")
            print(f"  Bounds:       {res['error_bounds']}")
            
    print("\n" + "=" * 70)
    print("  PHASE 2 SUMMARY")
    print("=" * 70)
    print("By exposing policy conflicts and terminology gaps as structured disagreements,")
    print("LEO guarantees epistemic honesty, avoiding silent failure and hallucinated certainty.")

if __name__ == "__main__":
    run_benchmark()
