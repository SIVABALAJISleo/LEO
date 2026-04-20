import time
import logging
from typing import Dict, Any, List

# Core Evolutionary Stack
from orchestration.ibie_engine import IBIE_Engine
from orchestration.ais_engine import AISEngine
from orchestration.compressed_dag import CompressedDAG

logger = logging.getLogger(__name__)

class HybridEngine_V3:
    """
    HYBRID DETERMINISTIC + ADAPTIVE ENGINE
    "You cannot remove computation from reasoning. You can only decide when to pay for it."
    
    1. FAST PATH: Deterministic, Branchless, SIMD (Constant Cost).
    2. SLOW PATH: Adaptive, Reasoning, Inference (Variable Cost).
    3. COMPILATION: Discoveries are structuralized and promoted to Fast Path.
    """
    def __init__(self):
        self.fast_path = IBIE_Engine()
        self.slow_path = AISEngine()
        self.dag = CompressedDAG()
        
        # Fast Path Promotion Registry
        # (Initially empty, populated by compilation loop)
        self.promotion_registry: Dict[str, str] = {}
        
        logger.info("Hybrid Engine V3 Online. Reasoning-cost management active.")

    def execute(self, query: str) -> Dict[str, Any]:
        """The Hybrid Reasoning Pipeline."""
        start = time.perf_counter()
        
        # --- PHASE 1: FAST PATH (Deterministic) ---
        # Direct check for known structural identities
        if query in self.promotion_registry:
            result = self.fast_path.resolve_invariant(query)
            return self._finalize(result, "HYBRID_FAST_PATH", start, query)
        
        # --- PHASE 2: SLOW PATH (Adaptive) ---
        # Unknown input. Pay for computation.
        logger.info(f"Hybrid: Unknown query detected. Executing Slow Path: {query[:30]}...")
        adaptive_result = self.slow_path.process_query(query)
        
        # --- PHASE 3: COMPILATION LOOP (Self-Optimization) ---
        # Structuralize the discovery for future O(1) resolution
        self._compile_discovery(query, adaptive_result['answer'])
        
        return self._finalize(
            {"result": [adaptive_result['answer']], "adaptive": True}, 
            "HYBRID_SLOW_PATH", 
            start,
            query
        )

    def _compile_discovery(self, query: str, answer: str):
        """Structurally encodes a slow-path discovery into the fast-path graph."""
        atom_id = self.dag.get_atom_id(query)
        result_id = self.dag.get_atom_id(answer)
        
        # Build DAG edge (no duplication)
        self.dag.create_node(atom_id, result_id)
        
        # Promote to Fast Path registry
        self.promotion_registry[query] = answer
        logger.info(f"Hybrid: Localized discovery compiled into structural memory: {query[:20]}")

    def _finalize(self, data: Dict[str, Any], technique: str, start: float, query: str) -> Dict[str, Any]:
        lat = (time.perf_counter() - start) * 1000
        return {
            "resolution": data.get("result", []),
            "hybrid_telemetry": {
                "pipeline": technique,
                "latency": f"{lat:.4f}ms",
                "is_adaptive": data.get("adaptive", False),
                "compiled_discovery": query in self.promotion_registry
            }
        }

if __name__ == "__main__":
    engine = HybridEngine_V3()
    
    q1 = "System status check"
    print(f"--- Run 1: Discovery Phase (Slow Path) ---")
    res1 = engine.execute(q1)
    print(res1)
    
    print(f"\n--- Run 2: Reified Execution (Fast Path) ---")
    res2 = engine.execute(q1)
    print(res2)

    q2 = "Chaos protocol 9 activation"
    print(f"\n--- Run 3: New Discovery (Slow Path) ---")
    print(engine.execute(q2))
