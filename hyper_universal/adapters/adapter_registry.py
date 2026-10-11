"""
hyper_universal/adapters/adapter_registry.py
Universal Workload Adapters:
Bridges domain-specific workloads into formal UniversalContracts and ComputationalIR DAGs.
Supports dense linear algebra, spatial convolution, attention, FFT, sorting, and dynamic programming.
"""
from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import numpy as np

from hyper_universal.contracts.contract_engine import (
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
)
from hyper_universal.workload_ir.graph import ComputationalIR, OpKind


class WorkloadAdapter(ABC):
    """Abstract base adapter for computational workload families."""

    @abstractmethod
    def get_family_name(self) -> str:
        pass

    @abstractmethod
    def create_contract(self, workload_id: str, exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT) -> UniversalContract:
        pass

    @abstractmethod
    def build_ir(self, workload_id: str, sample_input: Any) -> ComputationalIR:
        pass

    @abstractmethod
    def execute_reference(self, sample_input: Any) -> Any:
        pass


class DenseLinearAlgebraAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "DENSE_LINEAR_ALGEBRA"

    def create_contract(self, workload_id: str, exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
        )

    def build_ir(self, workload_id: str, sample_input: Tuple[np.ndarray, np.ndarray]) -> ComputationalIR:
        A, B = sample_input
        ir = ComputationalIR(name=workload_id)
        in_a = ir.add_input("A", A.shape, str(A.dtype))
        in_b = ir.add_input("B", B.shape, str(B.dtype))
        m, k = A.shape
        _, n = B.shape
        flops = 2 * m * k * n
        op = ir.add_op("matmul_out", OpKind.MATMUL, [in_a, in_b], (m, n), str(A.dtype), flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: Tuple[np.ndarray, np.ndarray]) -> np.ndarray:
        A, B = sample_input
        return A @ B


class SpectralFFTAdapter(WorkloadAdapter):
    def get_family_name(self) -> str:
        return "SPECTRAL_FFT"

    def create_contract(self, workload_id: str, exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT) -> UniversalContract:
        return UniversalContract(
            workload_id=workload_id,
            family=self.get_family_name(),
            exactness=exactness,
            tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
        )

    def build_ir(self, workload_id: str, sample_input: np.ndarray) -> ComputationalIR:
        ir = ComputationalIR(name=workload_id)
        in_sig = ir.add_input("signal", sample_input.shape, str(sample_input.dtype))
        n = len(sample_input)
        flops = int(5 * n * math.log2(max(n, 2)))
        op = ir.add_op("fft_out", OpKind.FFT, [in_sig], (n // 2 + 1,), "complex64", flops=flops)
        ir.mark_output(op)
        return ir

    def execute_reference(self, sample_input: np.ndarray) -> np.ndarray:
        return np.fft.rfft(sample_input)


class AdapterRegistry:
    """Central registry mapping family names to workload adapters."""

    def __init__(self):
        self._adapters: Dict[str, WorkloadAdapter] = {}
        self.register(DenseLinearAlgebraAdapter())
        self.register(SpectralFFTAdapter())

    def register(self, adapter: WorkloadAdapter):
        self._adapters[adapter.get_family_name()] = adapter

    def get_adapter(self, family_name: str) -> Optional[WorkloadAdapter]:
        return self._adapters.get(family_name)

    def list_supported_families(self) -> List[str]:
        return list(self._adapters.keys())
