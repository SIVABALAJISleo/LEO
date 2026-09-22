"""
hyper/discovery/search_space_compiler.py
========================================
Search Space Compiler for UCTDE (Phase 4).

Translates a workload and its application contract into a formal
TransformationSearchSpace defining:
- Legal vs illegal transformations
- Equivalence and precision constraints
- Side-effect and determinism boundaries
- Cost and resource models
- Transformation grammar and composition rules
Rule: Never permit illegal or contract-violating transformations.
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.universal.contracts.universal_contract import (
    UniversalContract,
    ContractCorrectness,
    PrecisionTier,
)


class TransformationSearchSpace(BaseModel):
    search_space_id: str = Field(default_factory=lambda: f"ss-{uuid.uuid4().hex[:8]}")
    workload_name: str
    legal_transformations: List[str] = Field(default_factory=list)
    illegal_transformations: List[str] = Field(default_factory=list)
    equivalence_constraints: Dict[str, Any] = Field(default_factory=dict)
    precision_constraints: Dict[str, Any] = Field(default_factory=dict)
    side_effect_constraints: Dict[str, Any] = Field(default_factory=dict)
    cost_model: Dict[str, Any] = Field(default_factory=dict)
    resource_model: Dict[str, Any] = Field(default_factory=dict)
    grammar_rules: List[str] = Field(default_factory=list)
    composition_rules: List[str] = Field(default_factory=list)

    def is_legal(self, transform_name: str) -> bool:
        return transform_name in self.legal_transformations and transform_name not in self.illegal_transformations


class SearchSpaceCompiler:
    """
    Compiles a formal transformation search space from workload context and contract.
    """

    ALL_TRANSFORMS = [
        "HORNER_POLYNOMIAL_REWRITE",
        "COMMON_SUBEXPRESSION_ELIMINATION",
        "MATRIX_ASSOCIATIVITY_REFACTOR",
        "COUNTING_SORT_DISPATCH",
        "DIVIDE_AND_CONQUER",
        "DYNAMIC_PROGRAMMING_MEMOIZATION",
        "SPARSE_CSR_CONVERSION",
        "LOW_RANK_SVD_FACTORIZATION",
        "INT8_SYMMETRIC_QUANTIZATION",
        "TERNARY_LUT_TMAC",
        "INCREMENTAL_DELTA_RESIDUAL",
        "CACHE_EXACT_LOOKUP",
        "OUTPUT_DIRECTED_QUICKSELECT",
        "L2_CACHE_TILING",
        "CPU_AVX2_SIMD_VECTORIZATION",
        "INTEL_IGPU_OPENCL_OFFLOAD",
        "HYBRID_CPU_IGPU_OVERLAP",
        "AST_SANDBOXED_PROGRAM_SYNTHESIS",
    ]

    def compile(
        self,
        workload_name: str,
        contract: UniversalContract,
        domain_hint: Optional[str] = None,
    ) -> TransformationSearchSpace:
        legal: List[str] = []
        illegal: List[str] = []

        # 1. Evaluate Precision & Exactness constraints
        is_strictly_exact = (
            contract.correctness in [ContractCorrectness.EXACT, ContractCorrectness.NUMERICAL]
            and contract.numeric_tolerance == 0.0
            and contract.relative_tolerance == 0.0
        )

        for t in self.ALL_TRANSFORMS:
            # Lossy transformations are strictly illegal when exactness is mandated
            if is_strictly_exact:
                if t in ["LOW_RANK_SVD_FACTORIZATION", "INT8_SYMMETRIC_QUANTIZATION", "TERNARY_LUT_TMAC"]:
                    illegal.append(t)
                    continue

            # Determinism checks
            if contract.deterministic and t in ["APPROXIMATE_STOCHASTIC_SAMPLING"]:
                illegal.append(t)
                continue

            legal.append(t)

        # 2. Grammar & composition rules
        grammar = [
            "INPUT -> PRE_TRANSFORM? -> CORE_KERNEL -> POST_TRANSFORM? -> OUTPUT",
            "PRE_TRANSFORM: [SPARSE_CONVERSION, TILING, QUANTIZATION]",
            "CORE_KERNEL: [HORNER, COUNTING_SORT, AVX2_GEMM, TMAC_LUT, SYMBOLIC]",
            "POST_TRANSFORM: [DEQUANTIZATION, RECONSTRUCTION]",
        ]

        composition = [
            "MAX_PIPELINE_DEPTH: 3",
            "ALLOW_PARALLEL_CPU_IGPU_SPLIT: TRUE",
            "ENFORCE_STRICT_SANDBOX: TRUE",
        ]

        # 3. Resource budget constraints
        resource_model = {
            "max_memory_mb": contract.memory_requirement_mb or 2048.0,
            "max_latency_ms": contract.latency_requirement_ms or 5000.0,
            "target_hardware": "Intel Core i5-12450H + Intel UHD 48EU iGPU",
            "measured_stream_bandwidth_gbs": 18.57,
        }

        cost_model = {
            "reference_cost_metric": "latency_ms",
            "optimization_objective": "minimize_operations_and_latency",
            "disallow_hardware_fabrication": True,
        }

        return TransformationSearchSpace(
            workload_name=workload_name,
            legal_transformations=legal,
            illegal_transformations=illegal,
            equivalence_constraints={"required_exactness": contract.correctness.value, "strict_exact": is_strictly_exact},
            precision_constraints={"precision_tier": contract.precision.value, "numeric_tolerance": contract.numeric_tolerance},
            side_effect_constraints={"allow_side_effects": contract.side_effects, "stateful": contract.stateful},
            cost_model=cost_model,
            resource_model=resource_model,
            grammar_rules=grammar,
            composition_rules=composition,
        )
