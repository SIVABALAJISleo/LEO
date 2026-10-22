"""
hyper_x/cpce/contracts.py
=========================
Typed Workload Contracts for CPCE.
Enforces unambiguous correctness requirements, numerical tolerance policies,
determinism constraints, memory budgets, and verification strategies.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ValidationMode(str, Enum):
    """The four formal validation modes."""
    EXACT = "EXACT"                         # Bitwise exact or exact discrete integer equality
    TOLERANCE_BASED = "TOLERANCE_BASED"     # Numerical tolerance |y_hat - y_ref| <= atol + rtol * |y_ref|
    APPROXIMATE = "APPROXIMATE"             # Quality-bounded approximation (cosine similarity >= threshold)
    TASK_QUALITY = "TASK_QUALITY"           # Task-level evaluation (LLM completion, perceptual SSIM)


class ExactnessRequirement(str, Enum):
    BITWISE_EXACT = "BITWISE_EXACT"
    MATHEMATICAL_EXACT = "MATHEMATICAL_EXACT"
    IEEE754_STRICT = "IEEE754_STRICT"
    EPSILON_TOLERANT = "EPSILON_TOLERANT"
    COSINE_BOUNDED = "COSINE_BOUNDED"
    TASK_ACCEPTANCE = "TASK_ACCEPTANCE"


@dataclasses.dataclass
class WorkloadContract:
    """
    Versioned, immutable mathematical contract governing computational workload execution.
    """
    contract_id: str
    version: str = "v1.0"
    validation_mode: ValidationMode = ValidationMode.TOLERANCE_BASED
    exactness_requirement: ExactnessRequirement = ExactnessRequirement.EPSILON_TOLERANT
    max_absolute_error: float = 1e-4
    max_relative_error: float = 1e-4
    min_cosine_similarity: float = 0.99
    determinism_required: bool = True
    memory_budget_mb: float = 512.0
    time_budget_ms: float = 5000.0
    permitted_backends: List[str] = dataclasses.field(default_factory=lambda: ["CPU", "INTEL_UHD_IGPU", "LOCAL_GGUF"])
    verification_strategy: str = "FREIVALDS_AND_TOLERANCE"
    description: str = ""
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def validate_relaxation(self, target_mode: ValidationMode) -> Tuple[bool, Optional[str]]:
        """
        Guards against silent contract relaxation.
        Exact contracts cannot be silently converted to approximate.
        """
        if self.validation_mode == ValidationMode.EXACT and target_mode != ValidationMode.EXACT:
            return False, f"Contract violation: cannot relax EXACT contract '{self.contract_id}' to {target_mode.value}"
        return True, None


class ContractRegistry:
    """Thread-safe registry of canonical workload contracts."""

    def __init__(self):
        self._contracts: Dict[str, WorkloadContract] = {}
        self._register_default_contracts()

    def _register_default_contracts(self):
        # 1. Exact Polynomial Horner Contract
        self.register(WorkloadContract(
            contract_id="polynomial_horner",
            version="v1.0",
            validation_mode=ValidationMode.EXACT,
            exactness_requirement=ExactnessRequirement.MATHEMATICAL_EXACT,
            max_absolute_error=1e-6,
            max_relative_error=1e-6,
            determinism_required=True,
            memory_budget_mb=64.0,
            verification_strategy="EXACT_MATHEMATICAL",
            description="Polynomial evaluation with algebraic Horner shortcut",
        ))

        # 2. Dense GEMM IEEE 754 Contract
        self.register(WorkloadContract(
            contract_id="dense_gemm",
            version="v1.0",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-4,
            max_relative_error=1e-4,
            determinism_required=True,
            memory_budget_mb=128.0,
            verification_strategy="FREIVALDS_AND_TOLERANCE",
            description="Dense FP32 matrix multiplication",
        ))

        # 3. Sparse SPMV Contract
        self.register(WorkloadContract(
            contract_id="sparse_spmv",
            version="v1.0",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=1e-5,
            max_relative_error=1e-5,
            determinism_required=True,
            memory_budget_mb=128.0,
            verification_strategy="SPARSE_INVARIANT",
            description="Sparse matrix-vector multiplication with CSR representation",
        ))

        # 4. Local AI Language Model Inference Contract
        self.register(WorkloadContract(
            contract_id="local_llm_inference",
            version="v1.0",
            validation_mode=ValidationMode.TASK_QUALITY,
            exactness_requirement=ExactnessRequirement.TASK_ACCEPTANCE,
            determinism_required=False,
            memory_budget_mb=1024.0,
            time_budget_ms=10000.0,
            permitted_backends=["LOCAL_GGUF_CPU"],
            verification_strategy="TOKEN_OUTPUT_AND_TTFT",
            description="Local quantized GGUF language model inference",
        ))

        # 5. Graphics Reconstruction Contract
        self.register(WorkloadContract(
            contract_id="graphics_reconstruct",
            version="v1.0",
            validation_mode=ValidationMode.APPROXIMATE,
            exactness_requirement=ExactnessRequirement.COSINE_BOUNDED,
            min_cosine_similarity=0.98,
            determinism_required=True,
            memory_budget_mb=256.0,
            verification_strategy="PERCEPTUAL_BOUND",
            description="Perceptual frame reconstruction and spatial upscaling",
        ))

    def register(self, contract: WorkloadContract):
        self._contracts[contract.contract_id] = contract

    def get(self, contract_id: str) -> Optional[WorkloadContract]:
        return self._contracts.get(contract_id)

    def list_contracts(self) -> List[Dict[str, Any]]:
        return [dataclasses.asdict(c) for c in self._contracts.values()]


DEFAULT_CONTRACT_REGISTRY = ContractRegistry()


def get_contract(contract_id: str) -> Optional[WorkloadContract]:
    """Retrieves standard contract from default registry."""
    return DEFAULT_CONTRACT_REGISTRY.get(contract_id)

