"""
hyper/escape_engine/execution/executor.py
=========================================
VAEE Unified Execution Dispatcher.
Routes candidate pathways to CPU or iGPU wrapped in execution sandboxing.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from ..pathways.schema import ComputationalPathway
from .sandbox import ExecutionSandbox
from .cpu_executor import CPUExecutor
from .igpu_executor import iGPUExecutor


class UnifiedExecutor:
    """Dispatches and measures candidate pathway execution."""

    def __init__(self) -> None:
        self.cpu = CPUExecutor()
        self.igpu = iGPUExecutor()
        self.sandbox = ExecutionSandbox()

    def execute_pathway(
        self,
        pathway: ComputationalPathway,
        input_data: Any,
        timeout_seconds: float = 5.0,
    ) -> Tuple[bool, Any, float, Optional[str]]:
        """
        Executes pathway.run_fn inside the sandbox.
        Returns: (success, result, latency_ms, error)
        """
        if pathway.run_fn is None:
            return False, None, 0.0, "Pathway has no executable run_fn bound"

        return self.sandbox.run_safe(
            pathway.run_fn,
            args=(input_data,),
            timeout_seconds=timeout_seconds,
        )
