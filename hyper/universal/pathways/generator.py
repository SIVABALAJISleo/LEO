"""
hyper/universal/pathways/generator.py
=====================================
Universal Pathway Generator.
Orchestrates candidate generation across all 10 transformation families:
1. Mathematical (Horner, Strassen, CSE)
2. Algorithmic (Non-comparative sort, DP rolling buffer)
3. Structural (Sparsity skipping, low-rank SVD)
4. Representation (INT8, BitNet b1.58 ternary)
5. Incremental (Memoization, delta)
6. Output-Directed (Top-K partial sorting, bounding box)
7. Memory (Cache tiling, buffer recycling)
8. Scheduling (CPU AVX2, iGPU OpenCL, Co-Execution)
9. Compiler (SIMD vectorization, strength reduction)
10. Program Synthesis (Safe AST synthesis)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from .schema import UniversalPathway, TransformationFamily
from .novelty import UniversalDiversityEngine
from .composition import UniversalPathwayComposer
from .mathematical import MathematicalTransformations
from .algorithmic import AlgorithmicTransformations
from .structural import StructuralTransformations
from .representation import RepresentationTransformations
from .incremental import IncrementalTransformations
from .output_directed import OutputDirectedTransformations
from .memory import MemoryTransformations
from .scheduling import SchedulingTransformations
from .compiler import CompilerTransformations
from .synthesis import ProgramSynthesizer
from ..adapter.workload_adapter import UniversalWorkload
from ..adapter.workload_types import WorkloadDomain
from ..contracts.universal_contract import UniversalContract
from ..information.boundary_engine import InformationBoundaryProfile


class UniversalPathwayGenerator:
    """Generates candidate computational pathways tailored to workload and contract properties."""

    def __init__(self, diversity_engine: Optional[UniversalDiversityEngine] = None, seed: int = 42) -> None:
        self.diversity_engine = diversity_engine or UniversalDiversityEngine()
        self.rng = random.Random(seed)

    def generate_candidate_pool(
        self,
        workload: UniversalWorkload,
        contract: UniversalContract,
        profile: Optional[InformationBoundaryProfile] = None,
        max_candidates: int = 20,
    ) -> List[UniversalPathway]:
        candidates: List[UniversalPathway] = []

        domain = workload.domain

        # 1. Mathematical Candidates
        if domain in (WorkloadDomain.NUMERICAL, WorkloadDomain.SCIENTIFIC_SIMULATION):
            coeffs = workload.metadata.get("coeffs")
            deg = len(coeffs) - 1 if coeffs is not None else 10
            candidates.append(MathematicalTransformations.create_horner_pathway(degree=deg, coeffs=coeffs))
            candidates.append(MathematicalTransformations.create_cse_pathway("numerical_cse"))
        elif domain in (WorkloadDomain.MATRIX_TENSOR, WorkloadDomain.MACHINE_LEARNING_INFERENCE):
            candidates.append(MathematicalTransformations.create_cse_pathway("tensor_cse"))

        # 2. Algorithmic Candidates
        if domain == WorkloadDomain.SEARCH_SORTING:
            k_max = workload.metadata.get("key_max", 1000)
            candidates.append(AlgorithmicTransformations.create_counting_sort_pathway(key_max=k_max))
        elif domain == WorkloadDomain.DYNAMIC_PROGRAMMING:
            candidates.append(AlgorithmicTransformations.create_dp_rolling_buffer_pathway(W=500))

        # 3. Structural Candidates
        if profile and profile.sparsity_ratio > 0.2:
            candidates.append(StructuralTransformations.create_sparsity_skipping_pathway(profile.sparsity_ratio))
        if domain in (WorkloadDomain.MATRIX_TENSOR, WorkloadDomain.MACHINE_LEARNING_INFERENCE, WorkloadDomain.IMAGE_VIDEO_PROCESSING):
            candidates.append(StructuralTransformations.create_low_rank_pathway(rank=16))

        # 4. Representation Candidates
        if not contract.is_exact():
            candidates.append(RepresentationTransformations.create_int8_quantization_pathway())
        candidates.append(RepresentationTransformations.create_ternary_bitnet_pathway())

        # 5. Incremental Candidates
        candidates.append(IncrementalTransformations.create_memoization_pathway(max_entries=512))
        candidates.append(IncrementalTransformations.create_delta_update_pathway())

        # 6. Output-Directed Candidates
        if domain == WorkloadDomain.SEARCH_SORTING or (profile and profile.has_output_directed_potential):
            candidates.append(OutputDirectedTransformations.create_topk_pathway(k=10))
        candidates.append(OutputDirectedTransformations.create_subregion_pathway())

        # 7. Memory Candidates
        candidates.append(MemoryTransformations.create_cache_tiling_pathway(tile_size=64))
        candidates.append(MemoryTransformations.create_buffer_recycling_pathway())

        # 8. Scheduling Candidates
        candidates.append(SchedulingTransformations.create_cpu_parallel_pathway(num_threads=8))
        candidates.append(SchedulingTransformations.create_igpu_opencl_pathway())
        candidates.append(SchedulingTransformations.create_coexecution_pathway(cpu_split=0.7))

        # 9. Compiler Candidates
        candidates.append(CompilerTransformations.create_simd_vectorization_pathway())
        candidates.append(CompilerTransformations.create_strength_reduction_pathway())

        # 10. Program Synthesis Candidates
        try:
            candidates.append(ProgramSynthesizer.synthesize_reduction_pathway("sum"))
        except Exception:
            pass

        # Register and filter novel candidates
        novel_candidates: List[UniversalPathway] = []
        for p in candidates:
            if self.diversity_engine.register(p):
                novel_candidates.append(p)
            if len(novel_candidates) >= max_candidates:
                break

        # Compositions if we have enough base candidates
        if len(novel_candidates) >= 2 and len(novel_candidates) < max_candidates:
            p_comp = UniversalPathwayComposer.compose(novel_candidates[0], novel_candidates[1])
            if self.diversity_engine.register(p_comp):
                novel_candidates.append(p_comp)

        return novel_candidates
