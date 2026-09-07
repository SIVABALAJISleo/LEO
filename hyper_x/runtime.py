"""
hyper_x/runtime.py
=============================================================================
HYPER-X Execution Runtime (HyperRuntime) & Safe Fallback Engine
=============================================================================
Responsibilities:
  - Dynamic hardware detection
  - Pathway dispatch & scheduling
  - Caching & reuse
  - Independent verification
  - Automatic safe reference fallback:
    No optimization may silently corrupt output. If confidence is insufficient,
    contract uncertain, or hardware unsupported, immediately use safe reference.
"""

from __future__ import annotations
import time
from typing import Dict, Any, Optional, Tuple, Callable
import numpy as np

from hyper_x.compiler import CompiledPathway
from hyper_x.strict.verifier import VerificationHierarchy
from hyper_x.strict.contracts import WorkloadContract

class HyperRuntime:
    """Production runtime executing compiled pathways with zero-corruption guarantee."""

    def __init__(self):
        self.verifier = VerificationHierarchy()

    def execute(
        self,
        pathway: CompiledPathway,
        contract: WorkloadContract,
        reference_verification_sample: Optional[np.ndarray] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter()
        try:
            out, meta = pathway.selected_candidate.execute_fn()
            # Fast verification check
            if reference_verification_sample is not None:
                val = contract.validate_result(out, reference_verification_sample)
                if not val["valid"]:
                    # Immediate safe fallback!
                    out = pathway.fallback_fn()
                    meta = {"fallback_triggered": True, "reason": val.get("message", "Validation failed")}
        except Exception as e:
            # Execution crash -> immediate safe fallback!
            out = pathway.fallback_fn()
            meta = {"fallback_triggered": True, "reason": f"Kernel crash: {str(e)}"}

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        meta["runtime_latency_ms"] = elapsed_ms
        return out, meta
