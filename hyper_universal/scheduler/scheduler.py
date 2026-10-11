"""
hyper_universal/scheduler/scheduler.py
Adaptive CPU/iGPU Heterogeneous Scheduler:
Routes execution across available CPU and Intel UHD iGPU compute backends
based on empirically measured cost models and memory transfer overheads.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple
import numpy as np

from hyper_omega.scheduler.heterogeneous import (
    IntelHardwareScheduler,
    HardwareTarget,
    SchedulingDecision,
)
from hyper_universal.backends.registry import BackendCapabilityRegistry
from hyper_universal.contracts.contract_engine import ContractRegistry


@dataclass
class ExecutionPlan:
    workload_id: str
    selected_backend: str
    fallback_backend: str
    data_size_bytes: int = 1024 * 1024


class UniversalScheduler:
    """Orchestrates heterogeneous execution selection."""

    def __init__(self):
        self.registry = BackendCapabilityRegistry()
        self.backend_registry = self.registry
        self.contract_registry = ContractRegistry()

    def schedule_workload(self, workload_id: str) -> ExecutionPlan:
        contract = self.contract_registry.get(workload_id)
        fallback = "CPU_AVX2"
        available = [b.backend_name for b in self.registry.get_available_backends()]

        # Select Intel UHD OpenCL if available and allowed, else CPU_AVX2
        if "INTEL_UHD_IGPU_OPENCL" in available:
            selected = "INTEL_UHD_IGPU_OPENCL"
        elif "CPU_AVX2" in available:
            selected = "CPU_AVX2"
        else:
            selected = fallback

        return ExecutionPlan(
            workload_id=workload_id,
            selected_backend=selected,
            fallback_backend=fallback,
        )

    def execute_with_fallback(
        self,
        primary_fn: Callable[..., Any],
        fallback_fn: Callable[..., Any],
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        primary_backend: str = "OPENCL_IGPU",
        fallback_backend: str = "CPU_AVX2",
    ) -> Tuple[Any, str, Optional[str]]:
        """
        Executes primary_fn on primary_backend.
        If any runtime exception occurs, catches it safely and invokes fallback_fn on fallback_backend.
        Returns: (result, used_backend, error_message_if_any)
        """
        kwargs = kwargs or {}
        try:
            res = primary_fn(*args, **kwargs)
            return res, primary_backend, None
        except Exception as e:
            err_msg = str(e)
            res = fallback_fn(*args, **kwargs)
            return res, fallback_backend, err_msg

    def schedule(
        self,
        workload_fn_cpu: Callable[[Any], Any],
        workload_fn_igpu: Optional[Callable[[Any], Any]],
        sample_input: Any,
        data_size_bytes: int = 1024 * 1024,
    ) -> SchedulingDecision:
        available_targets = self.registry.list_available_targets()

        if HardwareTarget.INTEL_UHD_IGPU_VULKAN not in available_targets and HardwareTarget.INTEL_UHD_IGPU_OPENCL not in available_targets:
            workload_fn_igpu = None

        decision = IntelHardwareScheduler.schedule_workload(
            workload_fn_cpu=workload_fn_cpu,
            workload_fn_igpu=workload_fn_igpu,
            sample_input=sample_input,
            data_size_bytes=data_size_bytes,
        )
        return decision
