"""
LEO v6 — The Independent Verifier
"LEO must never be allowed to declare success itself."
This module validates any LEO engine output against a canonical NumPy reference.
"""
import numpy as np
import time
from typing import Callable, Optional
from dataclasses import dataclass

@dataclass
class VerificationResult:
    passed: bool
    max_error: float
    mean_error: float
    contract_tolerance: float
    samples_checked: int
    latency_ms: float
    work_avoided_pct: float
    verdict: str

class IndependentVerifier:
    """
    The Iron Law Verifier.
    Randomly samples 5% of any output tensor and compares it against the 
    canonical reference (NumPy FP32). 
    
    The engine CANNOT declare success. Only the Verifier can.
    """
    SAMPLE_RATE = 0.05  # 5% sampling

    def verify(
        self,
        A: np.ndarray,
        B: np.ndarray,
        leo_output: np.ndarray,
        contract_tolerance: float = 1e-3,
        leo_latency_ms: float = 0.0,
        leo_ops: Optional[int] = None,
    ) -> VerificationResult:
        """
        Validates leo_output against a canonical reference for randomly sampled positions.
        """
        t0 = time.perf_counter()
        M, N = leo_output.shape

        # Determine number of samples
        n_samples = max(10, int(M * N * self.SAMPLE_RATE))

        # Pick random output positions to verify
        row_idx = np.random.randint(0, M, size=n_samples)
        col_idx = np.random.randint(0, N, size=n_samples)

        # Compute canonical reference for ALL sampled positions at once
        A64 = A.astype(np.float64)
        B64 = B.astype(np.float64)
        
        ref_values = np.array([
            float(np.dot(A64[r, :], B64[:, c]))
            for r, c in zip(row_idx, col_idx)
        ])
        leo_values = np.array([float(leo_output[r, c]) for r, c in zip(row_idx, col_idx)])
        
        # Use normalised absolute error: |leo - ref| / (|ref_scale| + eps)
        # ref_scale is the RMS of the reference values — avoids divide-by-zero on near-zero elements
        ref_scale = float(np.sqrt(np.mean(ref_values ** 2))) + 1e-10
        errors = np.abs(leo_values - ref_values) / ref_scale

        max_err = float(np.max(errors))
        mean_err = float(np.mean(errors))
        latency = (time.perf_counter() - t0) * 1000

        # Compute conventional FLOP count (2*M*N*K for a MxK x KxN GEMM)
        K = A.shape[1]
        conventional_ops = 2 * M * N * K
        actual_ops = leo_ops if leo_ops else conventional_ops
        work_avoided = max(0.0, 1.0 - actual_ops / conventional_ops) * 100.0

        passed = max_err <= contract_tolerance
        verdict = (
            f"PASS — Error {max_err:.2e} within tolerance {contract_tolerance:.1e}"
            if passed
            else f"FAIL — Error {max_err:.2e} EXCEEDS tolerance {contract_tolerance:.1e}"
        )

        return VerificationResult(
            passed=passed,
            max_error=max_err,
            mean_error=mean_err,
            contract_tolerance=contract_tolerance,
            samples_checked=n_samples,
            latency_ms=leo_latency_ms,
            work_avoided_pct=work_avoided,
            verdict=verdict,
        )

    def print_report(self, result: VerificationResult, mode: str = "UNKNOWN"):
        print(f"\n{'='*55}")
        print(f"  VERIFIER REPORT — Mode: {mode}")
        print(f"{'='*55}")
        print(f"  {'✅ PASS' if result.passed else '❌ FAIL'}")
        print(f"  Max Relative Error:   {result.max_error:.2e}")
        print(f"  Mean Relative Error:  {result.mean_error:.2e}")
        print(f"  Contract Tolerance:   {result.contract_tolerance:.1e}")
        print(f"  Samples Checked:      {result.samples_checked}")
        print(f"  Engine Latency:       {result.latency_ms:.2f} ms")
        print(f"  Work Avoided:         {result.work_avoided_pct:.1f}%")
        print(f"  Verdict: {result.verdict}")
        print(f"{'='*55}")
