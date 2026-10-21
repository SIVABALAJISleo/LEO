"""
hyper/upe/generator.py
======================
ENGINE 4: Alternative Pathway Generator.

Discovers and proposes alternative execution pathways for a given workload.
Every workload may evaluate candidate pathways across:
- Reference Baseline Implementation
- Algebraic Shortcuts (Horner, Matrix Chain, Strassen)
- Structured & Sparsity-Aware (2:4 AVX2, CSR)
- Operator Fusion (GEMM + Bias + ReLU)
- Memory-Bounded Streaming (Chunked GEMV, Online Softmax)
- Reduced Precision / Quantized (BitNet Ternary)
- Exact Memoization & Cache Lookup
"""

from __future__ import annotations

import dataclasses
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.upe.contract import WorkloadContract, ValidationMode
from hyper.upe.algebra import PathAlgebra, TransformationRule


@dataclasses.dataclass
class CandidatePathway:
    """A proposed execution pathway for a workload."""
    pathway_id: str
    workload_id: str
    rule_id: str
    candidate_name: str
    family: str
    estimated_flops: int
    estimated_memory_bytes: int
    estimated_speedup: float
    exactness_mode: str
    preconditions_met: bool
    rejection_reason: Optional[str] = None
    transform_fn: Optional[Callable[[Dict[str, Any]], Tuple[Any, Dict[str, Any]]]] = None
    fallback_fn: Optional[Callable[[Dict[str, Any]], Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway_id": self.pathway_id,
            "workload_id": self.workload_id,
            "rule_id": self.rule_id,
            "candidate_name": self.candidate_name,
            "family": self.family,
            "estimated_flops": self.estimated_flops,
            "estimated_memory_bytes": self.estimated_memory_bytes,
            "estimated_speedup": round(self.estimated_speedup, 2),
            "exactness_mode": self.exactness_mode,
            "preconditions_met": self.preconditions_met,
            "rejection_reason": self.rejection_reason,
        }


class AlternativePathwayGenerator:
    """
    Evaluates workload inputs and applicable transformation rules to generate valid candidate pathways.
    """

    def __init__(self, algebra: Optional[PathAlgebra] = None) -> None:
        self.algebra = algebra or PathAlgebra()

    def generate_candidates(
        self,
        contract: WorkloadContract,
        inputs: Dict[str, Any],
        max_candidates: int = 10,
    ) -> List[CandidatePathway]:
        """
        Generates candidate pathways for the workload.
        Filters out candidates that violate contract requirements or preconditions.
        Always includes the baseline reference pathway.
        """
        candidates: List[CandidatePathway] = []
        wid = contract.workload_id.lower()

        # 1. Baseline Reference Pathway (Always Available)
        cand_baseline = CandidatePathway(
            pathway_id=f"pw_base_{contract.workload_id}_{uuid.uuid4().hex[:6]}",
            workload_id=contract.workload_id,
            rule_id="baseline_reference",
            candidate_name="Baseline Trusted Reference",
            family="REFERENCE",
            estimated_flops=100_000,
            estimated_memory_bytes=1024 * 1024,
            estimated_speedup=1.0,
            exactness_mode="EXACT",
            preconditions_met=True,
            transform_fn=lambda inp: (np.dot(np.asarray(inp["A"]), np.asarray(inp["B"])) if "A" in inp and "B" in inp else 0.0, {}),
            fallback_fn=None,
        )
        candidates.append(cand_baseline)

        # 2. Match rules from PathAlgebra
        for rule in self.algebra.all_rules():
            # Check contract validation mode compatibility
            # Invariant: EXACT contract can never use APPROXIMATE rule
            if contract.validation_mode == ValidationMode.EXACT and rule.exactness_mode == "APPROXIMATE":
                continue

            # Evaluate applicability by workload signature
            preconditions_met = True
            rejection_reason = None
            speedup_est = 1.0
            flops_est = 50_000
            mem_est = 512 * 1024

            if rule.rule_id == "horner_polynomial_factorization":
                if "horner" in wid or "polynomial" in wid or "coefficients" in inputs:
                    speedup_est = 4.2
                    flops_est = 200
                else:
                    preconditions_met = False
                    rejection_reason = "Input does not contain polynomial coefficients"

            elif rule.rule_id == "prefix_sum_range_query":
                if "prefix" in wid or "range" in wid or "queries" in inputs:
                    speedup_est = 8.5
                    flops_est = 1_000
                else:
                    preconditions_met = False
                    rejection_reason = "Input does not match range-query structure"

            elif rule.rule_id == "fused_gemm_bias_relu":
                if "gemm" in wid or "linear" in wid or ("A" in inputs and "B" in inputs):
                    speedup_est = 1.6
                    flops_est = 80_000
                else:
                    preconditions_met = False
                    rejection_reason = "Input is not a matrix-matrix product"

            elif rule.rule_id == "sparsity_2_4_structured_acceleration":
                if "A" in inputs and isinstance(inputs["A"], np.ndarray):
                    sparsity = float(np.mean(np.abs(inputs["A"]) < 1e-5))
                    if sparsity >= 0.20:
                        speedup_est = 2.1
                        flops_est = int(100_000 * (1.0 - sparsity))
                    else:
                        preconditions_met = False
                        rejection_reason = f"Sparsity ratio {sparsity*100:.1f}% < 20% threshold"
                else:
                    preconditions_met = False
                    rejection_reason = "Matrix A not provided for sparsity inspection"

            elif rule.rule_id == "streaming_chunked_gemv":
                if "stream" in wid or ("A" in inputs and "v" in inputs):
                    speedup_est = 1.3
                    mem_est = 64 * 1024
                else:
                    preconditions_met = False
                    rejection_reason = "Input not formatted for chunked GEMV"

            elif rule.rule_id == "strassen_subcubic_decomposition":
                if "A" in inputs and isinstance(inputs["A"], np.ndarray):
                    n = inputs["A"].shape[0]
                    if n >= 64 and n % 2 == 0 and inputs["A"].shape == (n, n):
                        speedup_est = 1.45
                        flops_est = int(n ** 2.807)
                    else:
                        preconditions_met = False
                        rejection_reason = f"Matrix dimension {n} < 64 or not square even power"
                else:
                    preconditions_met = False
                    rejection_reason = "Not a square dense matrix"

            elif rule.rule_id == "bitnet_ternary_mma":
                if contract.validation_mode == ValidationMode.APPROXIMATE and ("W" in inputs or "A" in inputs):
                    speedup_est = 3.2
                    flops_est = 30_000
                else:
                    preconditions_met = False
                    rejection_reason = "Contract does not permit quality-bounded approximate MMA"

            elif rule.rule_id == "matrix_chain_associativity":
                if "matrix_chain" in wid or "chain" in wid or "matrices" in inputs or ("A" in inputs and "B" in inputs and "C" in inputs):
                    speedup_est = 3.8
                    flops_est = 15_000
                    mem_est = 256 * 1024
                else:
                    preconditions_met = False
                    rejection_reason = "Input does not contain matrix chain (requires 3+ matrices)"

            elif rule.rule_id == "kolmogorov_prng_inversion":
                if "kolmogorov" in wid or "prng" in wid or "seed" in inputs or "random" in wid:
                    speedup_est = 25.0
                    flops_est = 100
                    mem_est = 64
                else:
                    preconditions_met = False
                    rejection_reason = "Input is not a deterministic PRNG request (requires seed/count)"

            elif rule.rule_id == "welford_online_statistics":
                if "welford" in wid or "statistics" in wid or "data" in inputs or "variance" in wid:
                    speedup_est = 2.4
                    flops_est = 2_000
                    mem_est = 128
                else:
                    preconditions_met = False
                    rejection_reason = "Input is not a 1D observation sequence"

            elif rule.rule_id == "sliding_window_kv_cache":
                if "kv_cache" in wid or "sliding_window" in wid or "seq_len" in inputs:
                    speedup_est = 4.5
                    flops_est = 5_000
                    mem_est = 512 * 1024
                else:
                    preconditions_met = False
                    rejection_reason = "Input does not specify autoregressive sequence dimensions"

            elif rule.rule_id == "spherical_harmonic_radiance":
                if "spherical" in wid or "radiance" in wid or "normals" in inputs:
                    speedup_est = 42.0
                    flops_est = 500
                    mem_est = 64 * 1024
                else:
                    preconditions_met = False
                    rejection_reason = "Input does not contain 3D surface normal vectors"

            # Create candidate record
            cand = CandidatePathway(
                pathway_id=f"pw_{rule.rule_id}_{uuid.uuid4().hex[:6]}",
                workload_id=contract.workload_id,
                rule_id=rule.rule_id,
                candidate_name=rule.description,
                family=rule.family,
                estimated_flops=flops_est,
                estimated_memory_bytes=mem_est,
                estimated_speedup=speedup_est,
                exactness_mode=rule.exactness_mode,
                preconditions_met=preconditions_met,
                rejection_reason=rejection_reason,
                transform_fn=rule.transform_fn if preconditions_met else None,
                fallback_fn=rule.fallback_fn,
            )
            candidates.append(cand)

            if len(candidates) >= max_candidates:
                break

        return candidates
