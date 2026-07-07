import sys
import os
import time
import logging

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Core Subsystems
from hyper_runtime.semantic_replay.replay_cache import SemanticReplayCache
from hyper_runtime.novelty_estimation.novelty_estimator import NoveltyEstimationEngine
from hyper_runtime.sparse_routing.sparse_router import SparseIntelligenceRouter
from hyper_runtime.speculative_decoding.speculative_decoder import SpeculativeExecutionEngine
from hyper_runtime.benchmarking.telemetry_tracker import TelemetryTracker
from hyper_runtime.benchmarking.flop_estimator import FLOPsEstimator
from hyper_runtime.cpu_orchestrator.kernel_scheduler import CPUKernelOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("LEO.MVP_Pipeline")

class LEO_MVP_Pipeline:
    """
    LEO Runtime MVP: Local LLM Inference Optimizer
    Simulates the routing and compute-avoidance for Llama 3.1 8B GGUF.
    """
    def __init__(self):
        logger.info("Initializing LEO Adaptive Compute Minimization Runtime...")
        
        self.semantic_cache = SemanticReplayCache()
        self.novelty_estimator = NoveltyEstimationEngine()
        self.sparse_router = SparseIntelligenceRouter(hidden_dim=4096, total_layers=32)
        self.speculative_engine = SpeculativeExecutionEngine(k_draft_tokens=4, acceptance_rate=0.7)
        self.cpu_orchestrator = CPUKernelOrchestrator()
        
        self.telemetry = TelemetryTracker(log_dir=".hyper_cache/telemetry")
        self.flop_estimator = FLOPsEstimator(hidden_dim=4096, total_layers=32)
        
    def execute_query(self, query_id: str, prompt: str, target_length: int = 20) -> dict:
        t0 = time.perf_counter()
        import numpy as np
        
        # 1. Workload Analyzer & Semantic Cache Lookup
        import hashlib
        fingerprint = hashlib.sha256(prompt.encode()).hexdigest()
        np.random.seed(len(prompt))
        embedding = np.random.randn(384).astype(np.float32)
        response, confidence_score, match_type, _ = self.semantic_cache.search(prompt, fingerprint, embedding)
        
        # 2. Novelty & Entropy Estimator
        # Mocking context generation based on prompt length
        context_embeddings = [np.random.randn(384).astype(np.float32) for _ in range(3)]
        
        novelty_data = self.novelty_estimator.estimate_novelty(prompt, embedding, context_embeddings, time_since_last_seen=3600.0)
        routing_tier = novelty_data["routing_tier"]
        
        output_tokens = []
        fallback_triggered = False
        
        # Mocking input state for sparse routing later
        input_state = np.random.randn(1, len(prompt.split()), 4096).astype(np.float32)
        
        # 3. Adaptive Strategy Router
        if response is not None and confidence_score > 0.98:
            # PATH A: Semantic Replay (Zero Compute)
            route_taken = "Semantic Replay"
            logger.info(f"[{query_id}] Routed to: {route_taken}")
            output_tokens = response
            flop_data = self.flop_estimator.calculate_savings(True, 0, 0, 0, 0)
            
        elif routing_tier == "sparse_execution":
            # PATH B: Sparse Execution
            route_taken = "Sparse Execution"
            logger.info(f"[{query_id}] Routed to: {route_taken}")
            
            # CPU Pinning to P-Cores
            def _run_sparse():
                return self.sparse_router.route_execution(input_state)
            
            sparse_metrics = self.cpu_orchestrator.execute_dense_kernel(_run_sparse)
            output_tokens = [42] * target_length # Mock output
            
            flop_data = self.flop_estimator.calculate_savings(
                False, 
                sparse_metrics["tome_sparsity"],
                sparse_metrics["gating_sparsity"],
                sparse_metrics["moe_sparsity"],
                sparse_metrics["exit_layer"]
            )
            
        elif novelty_data["components"]["entropy"] < 0.6:
            # PATH C: Speculative Decoding (Low Novelty/Predictable)
            route_taken = "Speculative Decoding"
            logger.info(f"[{query_id}] Routed to: {route_taken}")
            
            spec_result = self.speculative_engine.generate(prompt, target_length)
            output_tokens = spec_result["tokens"]
            
            # Rough estimate: ~60% FLOPs saved due to draft model taking over
            flop_data = self.flop_estimator.calculate_savings(False, 0.5, 0.2, 0.0, 32)
            
        else:
            # PATH D: Exact Fallback (Irreducible Novelty)
            route_taken = "Exact Fallback"
            fallback_triggered = True
            logger.warning(f"[{query_id}] High Novelty/Low Confidence. Routed to: {route_taken}")
            
            # Simulate dense compute
            time.sleep(1.0)
            output_tokens = [99] * target_length
            flop_data = self.flop_estimator.calculate_savings(False, 0, 0, 0, 32)
            
        # Log to cache if it was novel
        if route_taken != "Semantic Replay":
            self.semantic_cache.add(prompt, fingerprint, embedding, output_tokens)
            
        latency = time.perf_counter() - t0
        
        # 4. Event Logging
        import psutil
        process = psutil.Process()
        self.telemetry.record_query(
            query_id, route_taken, latency, flop_data, 
            process.cpu_percent(), process.memory_info().rss / 1024**2
        )
        
        return {
            "query_id": query_id,
            "route_taken": route_taken,
            "latency_ms": latency * 1000,
            "flops_saved_ratio": flop_data["savings_ratio"],
            "fallback_triggered": fallback_triggered
        }

if __name__ == "__main__":
    pipeline = LEO_MVP_Pipeline()
    
    print("\n" + "=" * 70)
    print("  LEO RUNTIME MVP — ADAPTIVE INFERENCE PIPELINE")
    print("=" * 70)
    
    workloads = [
        ("q_001", "What is the capital of France?"),
        ("q_002", "Explain the significance of the 1997 Kyoto Protocol in detail."),
        ("q_003", "Write a python script to merge two dictionaries."),
        ("q_004", "What is the capital of France?"), # Should hit cache exactly
        ("q_005", "Write a highly novel proof for P vs NP using quantum topological invariants.") # Should fallback
    ]
    
    for q_id, prompt in workloads:
        print(f"\nProcessing: '{prompt}'")
        res = pipeline.execute_query(q_id, prompt)
        print(f"  -> Route: {res['route_taken']} | Latency: {res['latency_ms']:.2f}ms | Compute Avoided: {res['flops_saved_ratio']*100:.1f}%")
        
    print("\n[Exporting Final Metrics]")
    pipeline.telemetry.export_json()
    pipeline.telemetry.export_csv()
    
    report = pipeline.telemetry.generate_report()
    print("\n" + "=" * 70)
    print("  FINAL LEO MVP BENCHMARK REPORT")
    print("=" * 70)
    for k, v in report.items():
        print(f"{k.replace('_', ' ').title():<35}: {v}")
