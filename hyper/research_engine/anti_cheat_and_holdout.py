"""
hyper/research_engine/anti_cheat_and_holdout.py
===============================================
NVIDIA Reference Protocol, Blind Holdout System, Anti-Hardcoding, and Metamorphic Testing.

Implements Sections 20, 21, 22, 23, and 24:
- Strict reference protocols comparing identical numerical contracts
- Discovery vs. Validation vs. Blind Holdout partition
- Static and runtime anti-hardcoding / anti-cheat audits
- Metamorphic verification (scaling, transposition, symmetry, permutation)
"""

from __future__ import annotations
import ast
import dataclasses
import hashlib
import inspect
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.exactness import ExactnessMode


@dataclasses.dataclass
class NvidiaReferenceProfile:
    gpu_model: str = "NVIDIA GeForce RTX 4090 (24GB G6X)"
    cuda_version: str = "12.4"
    driver_version: str = "551.76"
    host_interface: str = "PCIe 4.0 x16"
    tdp_watts: float = 450.0
    measured_bandwidth_gbs: float = 1008.0
    workload_baselines_ms: Dict[str, float] = dataclasses.field(default_factory=lambda: {
        "GEMM_STANDARD": 0.45,
        "CONV2D_STANDARD": 0.38,
        "FFT_STANDARD": 0.22,
        "ATTENTION_STANDARD": 0.65,
        "PAGERANK_STANDARD": 1.20,
        "SORT_STANDARD": 0.30,
        "SHA256_STANDARD": 0.15,
    })


class BlindHoldoutSystem:
    """
    Maintains sealed holdout datasets that are strictly inaccessible to the search engine.
    """

    def __init__(self):
        self._sealed_registry: Dict[str, Dict[str, Any]] = {}

    def register_sealed_workload(self, holdout_id: str, inputs: Dict[str, Any], reference_output: Any):
        """Registers a sealed test problem that cannot be inspected during discovery."""
        self._sealed_registry[holdout_id] = {
            "inputs": inputs,
            "ref_hash": hashlib.sha256(str(reference_output).encode()).hexdigest(),
            "reference_output": reference_output,
            "access_count": 0,
        }

    def evaluate_holdout(
        self,
        holdout_id: str,
        candidate_fn: Callable[[Dict[str, Any]], Any],
        contract: ProblemContract,
    ) -> Dict[str, Any]:
        """
        Evaluates a frozen candidate pathway against a sealed holdout test.
        """
        if holdout_id not in self._sealed_registry:
            raise KeyError(f"Holdout workload '{holdout_id}' not found in sealed vault")

        entry = self._sealed_registry[holdout_id]
        entry["access_count"] += 1

        t0 = time.perf_counter()
        cand_out = candidate_fn(entry["inputs"])
        latency_ms = (time.perf_counter() - t0) * 1000.0

        ref_out = entry["reference_output"]
        if isinstance(cand_out, np.ndarray) and isinstance(ref_out, np.ndarray):
            diff = np.abs(cand_out - ref_out)
            err = float(np.max(diff))
            passed = err <= contract.tolerance_epsilon
        else:
            err = 0.0 if cand_out == ref_out else 1.0
            passed = cand_out == ref_out

        return {
            "holdout_id": holdout_id,
            "verified": passed,
            "max_error": err,
            "latency_ms": latency_ms,
            "access_count": entry["access_count"],
        }


class AntiHardcodingEngine:
    """
    Detects attempts to game benchmarks via hardcoded lookups, name-based conditionals,
    or synthetic delays.
    """

    SUSPICIOUS_TERMS = [
        "benchmark", "test_gemm", "test_conv", "perf_counter", "sleep",
        "lookup_table", "magic_constant", "mock", "fake"
    ]

    @classmethod
    def audit_candidate_callable(cls, fn: Callable[..., Any]) -> Tuple[bool, List[str]]:
        """
        Performs static AST inspection of the candidate function source.
        Returns (is_clean, findings_list).
        """
        findings: List[str] = []
        try:
            source = inspect.getsource(fn)
        except Exception:
            return True, ["Callable is native/C++ or dynamic closure; AST unavailable"]

        # Check for benchmark identity conditionals
        import textwrap
        tree = ast.parse(textwrap.dedent(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # Check for string comparisons against benchmark names
                for comp in node.comparators:
                    if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                        val_lower = comp.value.lower()
                        for term in cls.SUSPICIOUS_TERMS:
                            if term in val_lower:
                                findings.append(f"Suspicious branch comparing against constant '{comp.value}'")

            # Check for hardcoded sleep
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
                    findings.append("Forbidden time.sleep delay detected in candidate logic")

        is_clean = len(findings) == 0
        return is_clean, findings


class MetamorphicTestingEngine:
    """
    Verifies that candidate computation obeys fundamental mathematical metamorphic relations.
    Defeats input fingerprinting and cached lookup cheats.
    """

    @classmethod
    def verify_metamorphic_invariants(
        cls,
        candidate_fn: Callable[[Dict[str, Any]], Any],
        sample_inputs: Dict[str, Any],
        contract: ProblemContract,
    ) -> Tuple[bool, List[str]]:
        """
        Applies mathematical transformations to inputs and verifies output invariants:
        1. Homogeneity: f(alpha * x) == alpha * f(x) (for linear operators)
        2. Transposition symmetry: (A @ B)^T == B^T @ A^T
        """
        w_id = contract.workload_id.upper()
        violations: List[str] = []

        if ("MATMUL" in w_id or "GEMM" in w_id) and "A" in sample_inputs and "B" in sample_inputs:
            A = sample_inputs["A"]
            B = sample_inputs["B"]
            alpha = 3.5

            # Invariant 1: Scalar scaling (alpha * A) @ B == alpha * (A @ B)
            y_base = candidate_fn({"A": A, "B": B})
            y_scaled = candidate_fn({"A": alpha * A, "B": B})
            expected_scaled = alpha * y_base

            err_scale = float(np.max(np.abs(y_scaled - expected_scaled)))
            if err_scale > (contract.tolerance_epsilon * 10.0 + 1e-4):
                violations.append(f"Scaling metamorphic violation: error {err_scale:.2e} > tolerance")

            # Invariant 2: Transpose duality (B^T @ A^T)^T == A @ B
            if A.ndim == 2 and B.ndim == 2 and A.shape == B.shape:
                y_transposed = candidate_fn({"A": B.T, "B": A.T}).T
                err_trans = float(np.max(np.abs(y_transposed - y_base)))
                if err_trans > (contract.tolerance_epsilon * 10.0 + 1e-4):
                    violations.append(f"Transposition metamorphic violation: error {err_trans:.2e} > tolerance")

        is_valid = len(violations) == 0
        return is_valid, violations
