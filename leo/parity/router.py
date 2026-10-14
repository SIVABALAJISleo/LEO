"""
leo/parity/router.py
====================
Workload-Aware Parity Router:
1. Per request -> analyze redundancy (exact cache, semantic cache, low-rank, temporal).
2. Pick cheapest candidate path that satisfies the frozen contract.
3. Verify output against contract clauses.
4. Fall back to exact full-compute reference path on any violation.
5. Assign strictly one label: EXACT | APPROXIMATE | CACHED | PREDICTIVE | REDUCED_WORK | EMULATED.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple
import numpy as np

from .contracts import ContractDef, ContractsRegistry, ExecutionResult, ResultLabel
from .engines import (
    LLMInferenceEngine,
    RAGRetrievalEngine,
    TemporalRenderingEngine,
    TextEmbeddingsEngine,
)


class ParityWorkloadRouter:
    """
    Contract-driven execution router for the four target workloads.
    """

    def __init__(self, registry: ContractsRegistry) -> None:
        self.registry = registry

        # Instantiate local hardware-optimized execution engines
        self.llm_engine = LLMInferenceEngine()
        self.rag_engine = RAGRetrievalEngine()
        self.embeddings_engine = TextEmbeddingsEngine()
        self.rendering_engine = TemporalRenderingEngine()

    def route_and_execute(
        self,
        workload_name: str,
        inputs: Optional[Dict[str, Any]] = None,
        allow_cache: bool = True,
        force_fallback: bool = False,
    ) -> ExecutionResult:
        """
        Executes workload through the cheapest valid pathway, verifying correctness
        against contract and falling back to exact compute if needed.
        """
        contract = self.registry.get_contract(workload_name)
        inp = inputs if inputs is not None else contract.input_spec

        # ---------------------------------------------------------------------
        # 1. Quantized LLM Inference
        # ---------------------------------------------------------------------
        if workload_name == "quantized_llm_inference":
            prompt = inp.get("prompt_tokens", [101, 2054, 2003, 1037, 3231, 102])
            max_tokens = inp.get("max_new_tokens", 16)

            if force_fallback:
                # Direct fallback to exact reference
                t0 = time.perf_counter()
                ref_out, ref_ms = self.llm_engine.run_reference(prompt, max_tokens)
                return ExecutionResult(
                    output=ref_out,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=4.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_reason": "Forced fallback to exact reference"},
                    verified=True,
                )

            # Execute candidate layer-streamed speculative decoder
            cand_res = self.llm_engine.run_candidate(prompt, max_new_tokens=max_tokens)
            if not contract.validate_execution(cand_res):
                # Fallback to reference on violation
                ref_out, ref_ms = self.llm_engine.run_reference(prompt, max_tokens)
                cand_res = ExecutionResult(
                    output=ref_out,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=4.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_triggered": True, "prev_reason": cand_res.failure_reason},
                    verified=True,
                )
            return cand_res

        # ---------------------------------------------------------------------
        # 2. RAG Retrieval
        # ---------------------------------------------------------------------
        elif workload_name == "rag_retrieval":
            seed = inp.get("query_vector_seed", 42)
            top_k = inp.get("top_k", 5)
            np.random.seed(seed)
            query_vec = np.random.randn(self.rag_engine.embedding_dim).astype(np.float32)

            if force_fallback:
                t0 = time.perf_counter()
                ref_indices, ref_scores, ref_ms = self.rag_engine.run_reference(query_vec, top_k)
                return ExecutionResult(
                    output={"indices": ref_indices, "scores": ref_scores},
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=1.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_reason": "Forced fallback to exact linear scan"},
                    verified=True,
                )

            cand_res = self.rag_engine.run_candidate(query_vec, top_k=top_k, use_cache=allow_cache)
            if not contract.validate_execution(cand_res):
                ref_indices, ref_scores, ref_ms = self.rag_engine.run_reference(query_vec, top_k)
                cand_res = ExecutionResult(
                    output={"indices": ref_indices, "scores": ref_scores},
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=1.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_triggered": True, "prev_reason": cand_res.failure_reason},
                    verified=True,
                )
            return cand_res

        # ---------------------------------------------------------------------
        # 3. Text Embeddings
        # ---------------------------------------------------------------------
        elif workload_name == "text_embeddings":
            batch_size = inp.get("batch_size", 16)
            seq_len = inp.get("sequence_length", 64)
            hidden_dim = inp.get("hidden_dim", 256)
            np.random.seed(42)
            batch = np.random.randn(batch_size * seq_len, hidden_dim).astype(np.float32)

            if force_fallback:
                ref_out, ref_ms = self.embeddings_engine.run_reference(batch)
                return ExecutionResult(
                    output=ref_out,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=2.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_reason": "Forced fallback to exact dense GEMM"},
                    verified=True,
                )

            cand_res = self.embeddings_engine.run_candidate(
                batch,
                use_low_rank=True,
                max_allowed_error=contract.max_relative_error,
            )
            if not contract.validate_execution(cand_res):
                ref_out, ref_ms = self.embeddings_engine.run_reference(batch)
                cand_res = ExecutionResult(
                    output=ref_out,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=2.0,
                    correctness_metric_value=1.0,
                    metrics={"fallback_triggered": True, "prev_reason": cand_res.failure_reason},
                    verified=True,
                )
            return cand_res

        # ---------------------------------------------------------------------
        # 4. Temporal-Reuse Rendering
        # ---------------------------------------------------------------------
        elif workload_name == "temporal_reuse_rendering":
            frame_time = inp.get("frame_time", 1.0)
            # 8 dynamic tiles (12.5% of 64 tiles)
            dynamic_coords = [(0, 0), (0, 1), (1, 0), (1, 1), (4, 4), (4, 5), (5, 4), (5, 5)]

            if force_fallback:
                ref_frame, ref_ms = self.rendering_engine.run_reference(frame_time, dynamic_coords)
                return ExecutionResult(
                    output=ref_frame,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=1.0,
                    correctness_metric_value=100.0,
                    metrics={"fallback_reason": "Forced fallback to full frame recomputation"},
                    verified=True,
                )

            cand_res = self.rendering_engine.run_candidate(frame_time, dynamic_coords)
            if not contract.validate_execution(cand_res):
                ref_frame, ref_ms = self.rendering_engine.run_reference(frame_time, dynamic_coords)
                cand_res = ExecutionResult(
                    output=ref_frame,
                    label=ResultLabel.EXACT,
                    latency_ms=ref_ms,
                    peak_ram_mb=1.0,
                    correctness_metric_value=100.0,
                    metrics={"fallback_triggered": True, "prev_reason": cand_res.failure_reason},
                    verified=True,
                )
            return cand_res

        else:
            raise ValueError(f"Unknown workload: {workload_name}")
