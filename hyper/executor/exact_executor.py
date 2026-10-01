"""
hyper/executor/exact_executor.py
================================
UniversalExactExecutor for LEO/HYPER.
Fulfills Section 18:
"If no escape exists, execute the computation anyway under the defined semantic model."
Combines:
  1. Scalar Reference Backend (Infallible correctness oracle)
  2. Optimized CPU Backend (Genuine AVX2/FMA/SSE vectorization)
  3. Intel UHD Integrated GPU Backend (Genuine OpenVINO GPU runtime)
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper.universal_ir.program import UniversalIRProgram
from hyper.executor.reference_executor import UniversalReferenceExecutor
from hyper.backends.cpu_backend import CpuBackend
from hyper.backends.igpu_backend import IntelUhdBackend
from hyper.semantics.types import ExactnessLevel, VerificationVerdict


class UniversalExactExecutor:
    """
    Primary exact semantic executor.
    Executes any valid UniversalIRProgram under exact semantics using
    the best genuinely available hardware backend (CPU or Intel UHD iGPU),
    verified against the scalar reference oracle.
    """

    def __init__(self, prefer_igpu: bool = True) -> None:
        self.reference_backend = UniversalReferenceExecutor()
        self.cpu_backend = CpuBackend()
        self.igpu_backend = IntelUhdBackend()
        self.prefer_igpu = prefer_igpu
        self._verifier = None

    @property
    def verifier(self):
        if self._verifier is None:
            from hyper.verifier.differential_verifier import DifferentialVerifier
            self._verifier = DifferentialVerifier()
        return self._verifier

    def execute_exact(
        self,
        program: UniversalIRProgram,
        inputs: Dict[str, np.ndarray],
        exactness_level: ExactnessLevel = ExactnessLevel.EXACT_SEMANTIC,
    ) -> Tuple[Dict[str, np.ndarray], str, float]:
        """
        Executes program under exact semantics.
        Returns (outputs, backend_used, elapsed_ms).
        """
        program.validate()

        # Try Intel UHD iGPU if preferred and available
        if self.prefer_igpu and self.igpu_backend.is_available():
            try:
                outputs, elapsed_ms = self.igpu_backend.execute(program, inputs)
                # Verify exactness against reference
                report = self.verifier.verify(
                    program=program,
                    candidate_outputs=outputs,
                    inputs=inputs,
                    exactness_level=exactness_level,
                )
                if report.verdict == VerificationVerdict.PASS:
                    return outputs, "INTEL_UHD_IGPU", elapsed_ms
            except Exception:
                # Graceful fallback to CPU backend
                pass

        # Fallback to Optimized CPU Backend
        try:
            outputs, elapsed_ms = self.cpu_backend.execute(program, inputs)
            # Verify exactness
            report = self.verifier.verify(
                program=program,
                candidate_outputs=outputs,
                inputs=inputs,
                exactness_level=exactness_level,
            )
            if report.verdict == VerificationVerdict.PASS:
                return outputs, "CPU_OPTIMIZED_AVX2", elapsed_ms
        except Exception:
            pass

        # Infallible Scalar Reference Oracle fallback
        t0 = time.perf_counter()
        outputs = self.reference_backend.execute(program, inputs)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return outputs, "SCALAR_REFERENCE_ORACLE", elapsed_ms
