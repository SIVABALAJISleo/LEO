import sys
import os
import hashlib

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.semantic_memory.organizational_memory import OrganizationalSemanticMemory

def run_benchmark():
    print("=" * 70)
    print("  LEO RUNTIME — PHASE 4: ORGANIZATIONAL SEMANTIC MEMORY")
    print("=" * 70)
    
    memory = OrganizationalSemanticMemory()
    
    query = "Should we retain user log metadata for 7 years under EU guidelines?"
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    
    # 1. First encounter (Cold Start - No resolution in memory)
    print("[1] Query Cold Start: checking Organizational Semantic Memory...")
    decision = memory.retrieve_decision(query_hash)
    
    if not decision:
        print("  Memory MISS. Escalating to Governance Approval Chain...")
        
        # Simulate human compliance officer making a decision
        print("  [Human Intervention] Compliance Lead overrides and approves: 'Retain for 5 years'.")
        
        simulated_decision = {
            "query": query,
            "chosen_path": "Compliance Path A (GDPR Compliance)",
            "override_override": "Approved for 5 years maximum to satisfy GDPR data minimization.",
            "approved_by": "usr_compliance_lead_09",
            "confidence_geometry": 1.0
        }
        
        # Commit to memory
        memory.store_decision(query_hash, simulated_decision)
        
    # 2. Second encounter (Warmer query match)
    print("\n[2] Query Warm Run: checking Organizational Semantic Memory again...")
    decision = memory.retrieve_decision(query_hash)
    
    if decision:
        print("  Memory HIT! Retyping saved compliance decision instantly (Zero-Compute Replay):")
        payload = decision["decision"]
        print(f"    Approved Path:  {payload['chosen_path']}")
        print(f"    Decision Note:  {payload['override_override']}")
        print(f"    Auditor ID:     {payload['approved_by']}")
        
    print("\n" + "=" * 70)
    print("  PHASE 4 SUMMARY")
    print("=" * 70)
    print("By caching semantic resolutions in an immutable governance ledger, LEO ensures")
    print("that human-resolved policy disagreements become reusable organizational memory,")
    print("eliminating redundant reasoning work and guaranteeing absolute semantic consistency.")

if __name__ == "__main__":
    run_benchmark()
