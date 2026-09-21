"""
hyper/universal/execution/unified_runtime.py
============================================
Unified Execution Dispatcher.
Dynamically coordinates CPU, iGPU, and Co-Execution backends within sandboxed boundaries.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from .sandbox import UniversalSandbox
from .cpu_backend import CPUBackend
from .igpu_backend import iGPUBackend
from ..pathways.schema import UniversalPathway


class UnifiedRuntime:
    """Dispatches pathway execution to appropriate hardware backend under sandbox limits."""

    def __init__(self, sandbox_timeout_s: float = 15.0) -> None:
        self.sandbox = UniversalSandbox(default_timeout_s=sandbox_timeout_s)
        self.cpu_backend = CPUBackend()
        self.igpu_backend = iGPUBackend()

    def execute_pathway(
        self,
        pathway: UniversalPathway,
        input_data: Any,
    ) -> Tuple[bool, Optional[Any], float, Optional[str]]:
        fn = pathway.run_fn
        if fn is None:
            return False, None, 0.0, f"Pathway {pathway.pathway_id} has no executable run_fn"

        hw = pathway.target_hardware
        if hw == "INTEL_UHD_IGPU" and self.igpu_backend.opencl_available:
            exec_fn = lambda x: self.igpu_backend.execute(fn, x)[0]
        else:
            exec_fn = lambda x: self.cpu_backend.execute(fn, x)[0]

        return self.sandbox.run_safe(exec_fn, input_data)
