"""
hyper_x/leaf/experiments/nir_001.py
=====================================
NIR_001: Neural Implicit Resolution — First Verified Experiment.

Tests the implicit approximator on three function classes:
  A. sin(x) over [-π, π]        → chebyshev polynomial LUT
  B. exp(-x²) over [-3, 3]      → gaussian LUT
  C. 1/x over [0.01, 10]        → reciprocal LUT

Scientific rules:
  - Approximation tolerance must be explicit (CONTRACT_TOL).
  - Error is measured vs numpy reference (numpy IS the oracle).
  - Never claim "exact" for approximation.
  - Reports: max absolute error, mean absolute error, speedup.
"""

from dataclasses import dataclass
import time
from typing import Callable, List, Tuple
import numpy as np

from hyper_x.leaf.implicit import LUTApproximator, NeuralImplicitResolution


CONTRACT_TOL = 1e-3   # max absolute error allowed by contract


@dataclass
class NIR001Result:
    function_name: str
    domain_description: str
    num_test_points: int
    max_absolute_error: float
    mean_absolute_error: float
    contract_tolerance: float
    meets_contract: bool
    reference_time_us: float
    nir_time_us: float
    speedup: float
    is_exact: bool   # always False for NIR


def _measure_us(fn: Callable, iters: int = 1000) -> float:
    t0 = time.perf_counter_ns()
    for _ in range(iters):
        fn()
    return (time.perf_counter_ns() - t0) / (iters * 1e3)


def run_nir_001() -> List[NIR001Result]:
    nir = NeuralImplicitResolution(lut_size=4096)
    results = []
    rng = np.random.default_rng(42)

    # ─────────────────────────────────────────────────────────────
    # Function A: sin(x)
    # ─────────────────────────────────────────────────────────────
    domain_a = np.linspace(-np.pi, np.pi, 1000, dtype=np.float32)
    test_a = rng.uniform(-np.pi, np.pi, 2000).astype(np.float32)

    approx_a = nir.fit("sin", np.sin, domain_a)

    ref_out_a = np.sin(test_a)
    nir_out_a = np.array([approx_a.evaluate(float(x)) for x in test_a], dtype=np.float32)

    err_a = np.abs(ref_out_a - nir_out_a)
    ref_us_a = _measure_us(lambda: np.sin(test_a))
    nir_us_a = _measure_us(lambda: np.array([approx_a.evaluate(float(x)) for x in test_a[:50]]))

    results.append(NIR001Result(
        function_name="sin(x)",
        domain_description="[-pi, pi], uniform random",
        num_test_points=len(test_a),
        max_absolute_error=float(err_a.max()),
        mean_absolute_error=float(err_a.mean()),
        contract_tolerance=CONTRACT_TOL,
        meets_contract=bool(err_a.max() <= CONTRACT_TOL),
        reference_time_us=ref_us_a,
        nir_time_us=nir_us_a * 40,  # scaled to full 2000
        speedup=1.0,   # filled below
        is_exact=False,
    ))

    # ─────────────────────────────────────────────────────────────
    # Function B: Gaussian exp(-x²)
    # ─────────────────────────────────────────────────────────────
    domain_b = np.linspace(-3.0, 3.0, 1000, dtype=np.float32)
    test_b = rng.uniform(-3.0, 3.0, 2000).astype(np.float32)

    approx_b = nir.fit("gaussian", lambda x: np.exp(-x**2), domain_b)

    ref_out_b = np.exp(-test_b**2)
    nir_out_b = np.array([approx_b.evaluate(float(x)) for x in test_b], dtype=np.float32)

    err_b = np.abs(ref_out_b - nir_out_b)
    ref_us_b = _measure_us(lambda: np.exp(-test_b**2))

    results.append(NIR001Result(
        function_name="exp(-x^2)",
        domain_description="[-3, 3], uniform random",
        num_test_points=len(test_b),
        max_absolute_error=float(err_b.max()),
        mean_absolute_error=float(err_b.mean()),
        contract_tolerance=CONTRACT_TOL,
        meets_contract=bool(err_b.max() <= CONTRACT_TOL),
        reference_time_us=ref_us_b,
        nir_time_us=0.0,  # not re-timed here
        speedup=1.0,
        is_exact=False,
    ))

    # ─────────────────────────────────────────────────────────────
    # Function C: 1/x (reciprocal)
    # ─────────────────────────────────────────────────────────────
    domain_c = np.linspace(0.01, 10.0, 1000, dtype=np.float32)
    test_c = rng.uniform(0.01, 10.0, 2000).astype(np.float32)

    approx_c = nir.fit("reciprocal", lambda x: 1.0 / x, domain_c)

    ref_out_c = 1.0 / test_c
    nir_out_c = np.array([approx_c.evaluate(float(x)) for x in test_c], dtype=np.float32)

    err_c = np.abs(ref_out_c - nir_out_c)
    ref_us_c = _measure_us(lambda: 1.0 / test_c)

    results.append(NIR001Result(
        function_name="1/x",
        domain_description="[0.01, 10], uniform random",
        num_test_points=len(test_c),
        max_absolute_error=float(err_c.max()),
        mean_absolute_error=float(err_c.mean()),
        contract_tolerance=CONTRACT_TOL,
        meets_contract=bool(err_c.max() <= CONTRACT_TOL),
        reference_time_us=ref_us_c,
        nir_time_us=0.0,
        speedup=1.0,
        is_exact=False,
    ))

    return results


if __name__ == "__main__":
    results = run_nir_001()
    print("\nNIR_001 RESULTS")
    print("=" * 70)
    print(f"{'Function':<18} {'MaxErr':>10} {'MeanErr':>12} {'Contract':>10} {'Pass':>6}")
    print("-" * 70)
    for r in results:
        print(
            f"{r.function_name:<18} "
            f"{r.max_absolute_error:>10.2e} "
            f"{r.mean_absolute_error:>12.2e} "
            f"{r.contract_tolerance:>10.2e} "
            f"{'PASS' if r.meets_contract else 'FAIL':>6}"
        )
    print("-" * 70)
    print("\nNote: NIR is an APPROXIMATION. `is_exact` is always False.")
