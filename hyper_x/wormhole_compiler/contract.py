"""
hyper_x/wormhole_compiler/contract.py
=============================================================================
HYPER-X Contract Compiler: The Source of Truth for Workload Requirements
=============================================================================
Compiles, validates, and enforces formal workload contracts before any search
or compilation is performed. Ensures that candidate shortcuts respect exactness,
numerical tolerance, latency SLOs, memory limits, and cache policies.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List
from hyper_x.wormhole_compiler.schemas import (
    WorkloadContract,
    CorrectnessRequirement,
    CachePolicy,
    ExecutionTrack,
)


class ContractViolationError(Exception):
    """Raised when a candidate execution or configuration violates contract constraints."""
    pass


class ContractCompiler:
    """Compiles domain parameters and user specifications into immutable WorkloadContracts."""

    @staticmethod
    def compile_matrix_contract(
        workload_id: str,
        shape: Tuple[int, int, int],  # (M, K, N)
        dtype: str = "float32",
        correctness: CorrectnessRequirement = CorrectnessRequirement.NUMERICAL_TOLERANCE,
        tolerance: float = 1e-4,
        latency_slo_ms: float = 100.0,
        memory_limit_mb: float = 4096.0,
        cache_policy: CachePolicy = CachePolicy.COLD,
        execution_track: ExecutionTrack = ExecutionTrack.APPLICATION_CONTRACT,
        acceptable_approximations: Optional[List[str]] = None,
        forbidden_approximations: Optional[List[str]] = None
    ) -> WorkloadContract:
        M, K, N = shape
        return WorkloadContract(
            workload_id=workload_id,
            operation="matrix_multiply",
            input_shape=(M, K),
            output_shape=(M, N),
            dtype=dtype,
            correctness=correctness,
            tolerance=tolerance,
            latency_slo_ms=latency_slo_ms,
            throughput_slo=1000.0 / max(0.001, latency_slo_ms),
            memory_limit_mb=memory_limit_mb,
            power_limit_watts=None,
            quality_requirement=1.0 if correctness == CorrectnessRequirement.EXACT else (1.0 - tolerance),
            determinism=True,
            reproducibility=True,
            acceptable_approximations=acceptable_approximations or ["low_rank", "sparsity", "quantization", "delta"],
            forbidden_approximations=forbidden_approximations or ["unverified_zeroing", "unbounded_truncation"],
            cache_policy=cache_policy,
            execution_track=execution_track,
            hardware_constraints={"target_isa": ["AVX2", "FMA"], "max_threads": 8}
        )

    @staticmethod
    def compile_graphics_contract(
        workload_id: str,
        resolution: Tuple[int, int],  # (H, W)
        target_fps: float = 60.0,
        min_ssim: float = 0.92,
        min_psnr_db: float = 28.0,
        cache_policy: CachePolicy = CachePolicy.WARM,
        execution_track: ExecutionTrack = ExecutionTrack.APPLICATION_CONTRACT
    ) -> WorkloadContract:
        H, W = resolution
        budget_ms = 1000.0 / target_fps
        return WorkloadContract(
            workload_id=workload_id,
            operation="graphics_denoising_reconstruction",
            input_shape=(H, W, 3),
            output_shape=(H, W, 3),
            dtype="float32",
            correctness=CorrectnessRequirement.PERCEPTUAL,
            tolerance=1.0 - min_ssim,
            latency_slo_ms=budget_ms,
            throughput_slo=target_fps,
            memory_limit_mb=2048.0,
            quality_requirement=min_ssim,
            determinism=False,
            reproducibility=True,
            acceptable_approximations=["temporal_reprojection", "event_driven_deltas", "bilateral_filter", "hierarchical_coarse"],
            forbidden_approximations=["black_frame", "frozen_state_without_check"],
            cache_policy=cache_policy,
            execution_track=execution_track,
            hardware_constraints={"target_fps": target_fps, "min_psnr_db": min_psnr_db}
        )

    @staticmethod
    def compile_stencil_contract(
        workload_id: str,
        grid_shape: Tuple[int, int],
        tolerance: float = 1e-3,
        latency_slo_ms: float = 50.0,
        cache_policy: CachePolicy = CachePolicy.COLD
    ) -> WorkloadContract:
        return WorkloadContract(
            workload_id=workload_id,
            operation="scientific_stencil_diffusion",
            input_shape=grid_shape,
            output_shape=grid_shape,
            dtype="float32",
            correctness=CorrectnessRequirement.NUMERICAL_TOLERANCE,
            tolerance=tolerance,
            latency_slo_ms=latency_slo_ms,
            throughput_slo=1000.0 / max(0.001, latency_slo_ms),
            memory_limit_mb=1024.0,
            quality_requirement=1.0 - tolerance,
            determinism=True,
            reproducibility=True,
            acceptable_approximations=["multigrid", "fft_spectral", "subgrid_delta"],
            forbidden_approximations=["unstable_divergence"],
            cache_policy=cache_policy,
            execution_track=ExecutionTrack.APPLICATION_CONTRACT
        )

    @staticmethod
    def validate_candidate_against_contract(
        contract: WorkloadContract,
        candidate_latency_ms: float,
        candidate_error: float,
        candidate_memory_mb: float,
        used_approximations: List[str]
    ) -> Tuple[bool, List[str]]:
        violations = []
        
        # 1. Exactness / Numerical tolerance
        if contract.correctness == CorrectnessRequirement.EXACT and candidate_error > 0.0:
            violations.append(f"Contract demands EXACT output, but candidate error is {candidate_error:.2e}")
        elif candidate_error > contract.tolerance:
            violations.append(f"Candidate error {candidate_error:.2e} exceeds contract tolerance {contract.tolerance:.2e}")

        # 2. Latency SLO
        if candidate_latency_ms > contract.latency_slo_ms:
            violations.append(f"Candidate latency {candidate_latency_ms:.2f}ms exceeds SLO {contract.latency_slo_ms:.2f}ms")

        # 3. Memory limit
        if candidate_memory_mb > contract.memory_limit_mb:
            violations.append(f"Candidate memory {candidate_memory_mb:.1f}MB exceeds limit {contract.memory_limit_mb:.1f}MB")

        # 4. Forbidden approximations check
        for approx in used_approximations:
            if approx in contract.forbidden_approximations:
                violations.append(f"Candidate used forbidden approximation: '{approx}'")

        return len(violations) == 0, violations
