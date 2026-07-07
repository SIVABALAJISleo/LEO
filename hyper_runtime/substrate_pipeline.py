import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hashlib
import logging
from typing import Dict, Any

from hyper_runtime.primitive_decomposition.decomposition_engine import PrimitiveDecompositionEngine
from hyper_runtime.semantic_action_protocol.sap_engine import SAPEngine
from hyper_runtime.context_momentum.thread_manager import ContextThreadManager
from hyper_runtime.context_momentum.momentum_prefetcher import MomentumPrefetcher
from hyper_runtime.semantic_memory.organizational_memory import OrganizationalSemanticMemory
from hyper_runtime.entropy_governance.entropy_governor import LEOEntropyGovernor
from hyper_runtime.entropy_governance.observability_tracer import LEOTracer

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("LEO.SubstratePipeline")

class LEOSubstratePipeline:
    """
    LEO — Semantic Workflow Execution Substrate
    
    A unified runtime integrating Phases 1–5 into a single observable,
    auditable enterprise cognition pipeline.
    """
    def __init__(self):
        self.decomposer = PrimitiveDecompositionEngine()
        self.sap = SAPEngine()
        self.thread_manager = ContextThreadManager()
        self.prefetcher = MomentumPrefetcher()
        self.memory = OrganizationalSemanticMemory()
        self.governor = LEOEntropyGovernor()
        self.tracer = LEOTracer()
        
        # Prepopulate active threads
        self.thread_manager.create_thread("thread_001", "legal", "Initial query")
        self.thread_manager.create_thread("thread_002", "tax", "Initial ledger query")
        
    def execute_workflow(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        trace_id = self.tracer.start_span(query)
        
        # 1. Query Taming & Workload Classification
        logger.info("Step 1: Running Workload Eligibility Classifier...")
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        
        # 2. Decompose into Stable Primitives (Phase 1)
        res_decomp = self.decomposer.decompose(query)
        if res_decomp["primitive_gap"]:
            err_msg = f"Execution Blocked! Query falls outside eligible enterprise cognition domain."
            self.tracer.log_routing_event(trace_id, "Workload Classifier", {"status": "BLOCKED", "reason": err_msg})
            return {"status": "BLOCKED", "reason": err_msg, "trace_id": trace_id}
            
        self.tracer.log_routing_event(trace_id, "Primitive Decomposition", {
            "status": "SUCCESS",
            "primitives": [p["primitive"] for p in res_decomp["pipeline"]],
            "ambiguity_rate": res_decomp["ambiguity_rate"]
        })
        
        # 3. Context Thread Management (Phase 3)
        target_thread = self.thread_manager.detect_thread_switch(query)
        if target_thread:
            self.thread_manager.switch_to_thread(target_thread)
            self.tracer.log_routing_event(trace_id, "Context Switch", {"switched_to": target_thread})
            
        # 4. Semantic Action Protocol & Memory Replay (Phase 2 & 4)
        sap_result = self.sap.analyze_semantic_alignment(query, context)
        if sap_result["status"] == "CONTESTED":
            # Check if this exact disagreement has already been resolved in memory
            decision = self.memory.retrieve_decision(query_hash)
            if decision:
                logger.info("Found human-approved decision in Organizational Semantic Memory. Replaying...")
                self.tracer.log_routing_event(trace_id, "Memory Replay", {
                    "status": "SUCCESS",
                    "source": "Organizational Memory",
                    "override_override": decision["decision"]["override_override"]
                })
                return {
                    "status": "SUCCESS",
                    "resolution_path": "Replayed from Semantic Memory",
                    "output": decision["decision"]["override_override"],
                    "trace_id": trace_id
                }
            else:
                # Escalate conflict
                self.tracer.log_routing_event(trace_id, "SAP Conflict Escalation", {
                    "status": "ESCALATED",
                    "disagreement_type": sap_result["disagreement"]["type"]
                })
                return {
                    "status": "ESCALATED",
                    "reason": sap_result["disagreement"]["description"],
                    "trace_id": trace_id
                }
                
        # 5. Core Pipeline execution (Phase 5 Governance)
        # Mocking values for pipeline operators
        cost = {"estimated_flops": 5.0e8}
        contract = ["standard_execution_output"]
        
        try:
            self.governor.assert_execution_preconditions(cost, contract)
            self.tracer.log_routing_event(trace_id, "Governance Enforcement", {"status": "SUCCESS"})
        except Exception as e:
            return {"status": "GOVERNANCE_BLOCKED", "reason": str(e), "trace_id": trace_id}
            
        # 6. Momentum Prefetching (Phase 3)
        if len(res_decomp["pipeline"]) > 0:
            first_prim = res_decomp["pipeline"][0]["primitive"]
            self.prefetcher.prefetch(first_prim)
            self.tracer.log_routing_event(trace_id, "Momentum Prefetching", {
                "status": "SUCCESS",
                "prewarmed": self.prefetcher.get_warmed()
            })
            
        # Final success
        return {
            "status": "SUCCESS",
            "resolution_path": "Deterministic Routing Engine",
            "trace_id": trace_id
        }
        
if __name__ == "__main__":
    print("=" * 70)
    print("  LEO RUNTIME — MASTER WORKFLOW SUBSTRATE PIPELINE")
    print("=" * 70)
    
    pipeline = LEOSubstratePipeline()
    
    # Run a test workflow
    q = "Audit the procurement contract to extract liability clauses."
    print(f"\nProcessing Query: '{q}'")
    res = pipeline.execute_workflow(q, {})
    
    print(f"\nPipeline Execution Result:")
    for k, v in res.items():
        print(f"  {k:<20}: {v}")
        
    print("\n" + "=" * 70)
    print("  END OF RUN")
    print("=" * 70)
