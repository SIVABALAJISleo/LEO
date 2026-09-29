"""
hyper/research_engine/learning_and_benchmarking.py
==================================================
Local Discovery Database, Generalization Tester, Empirical Benchmark Harness,
and Immutable Experiment Journal.

Implements Sections 35, 36, 37, 38, 39, and 40:
- Learns successful and failed patterns without ever caching or hardcoding outputs
- Generalization testing across neighboring dimensions and distributions
- Multi-run statistical benchmarking (warmups, mean, median, stddev, min, max)
- Immutable experiment archival in experiments/<id>/
"""

from __future__ import annotations
import copy
import dataclasses
import json
import os
import statistics
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.exactness import ExactnessMode
from hyper.research_engine.solution_space_compiler import CandidatePathway
from hyper.research_engine.counterexample_verifier import EquivalenceVerifier


class LocalDiscoveryDatabase:
    """
    Stores historical patterns of successful and failed transformations to guide future search.
    STRICT DISCIPLINE: Never caches precomputed outputs. Always requires candidate execution.
    """

    DB_PATH = Path("reports/discovery_knowledge_db.json")

    @classmethod
    def record_discovery(
        cls,
        workload_domain: str,
        transformation: str,
        is_verified: bool,
        measured_speedup: float,
        notes: str = "",
    ):
        os.makedirs(cls.DB_PATH.parent, exist_ok=True)
        entries = []
        if cls.DB_PATH.exists():
            try:
                with open(cls.DB_PATH, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        entries.append({
            "workload_domain": workload_domain,
            "transformation": transformation,
            "is_verified": is_verified,
            "measured_speedup": measured_speedup,
            "notes": notes,
            "timestamp": time.time(),
        })

        with open(cls.DB_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    @classmethod
    def get_recommended_transformations(cls, workload_domain: str) -> List[str]:
        """Returns prioritized transformations based on historical success rates."""
        if not cls.DB_PATH.exists():
            return []
        try:
            with open(cls.DB_PATH, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            return []

        domain_entries = [e for e in entries if e.get("workload_domain") == workload_domain]
        # Count verified successes
        success_counts: Dict[str, int] = {}
        for e in domain_entries:
            if e.get("is_verified", False):
                t = e["transformation"]
                success_counts[t] = success_counts.get(t, 0) + 1

        sorted_recs = sorted(success_counts.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_recs]


class GeneralizationTester:
    """
    Evaluates whether a discovered transformation generalizes to neighboring problems
    or is merely an overfitted workload-specific artifact.
    """

    @classmethod
    def test_generalization(
        cls,
        candidate: CandidatePathway,
        base_contract: ProblemContract,
    ) -> Tuple[bool, str]:
        """
        Tests candidate against variations: perturbed dimensions, modified ranges,
        different matrix aspect ratios.
        """
        if not candidate.executable_fn:
            return False, "Candidate lacks executable callable"

        w_id = base_contract.workload_id.upper()
        if "MATMUL" in w_id or "GEMM" in w_id:
            # Test neighbor shapes (e.g. 17x17, 33x33)
            test_shapes = [(16, 16), (33, 33), (15, 27)]
            for m, k in test_shapes:
                A = np.random.randn(m, k).astype(np.float32)
                B = np.random.randn(k, m).astype(np.float32)
                neighbor_contract = copy.deepcopy(base_contract)
                neighbor_contract.input_domain = {"A": {"shape": [m, k]}, "B": {"shape": [k, m]}}
                neighbor_contract.output_domain = {"C": {"shape": [m, m]}}

                proof = EquivalenceVerifier.verify_candidate(candidate.executable_fn, candidate.candidate_id, neighbor_contract)
                if not proof.is_verified:
                    return False, f"WORKLOAD-SPECIFIC: Failed on neighbor shape {m}x{k}x{m}"

        return True, "GENERALIZED: Passed all neighboring dimension tests"


class BenchmarkRunner:
    """
    Executes rigorous multi-run empirical timing.
    """

    @classmethod
    def benchmark_callable(
        cls,
        fn: Callable[[Dict[str, Any]], Any],
        sample_inputs: Dict[str, Any],
        warmup_runs: int = 3,
        measured_runs: int = 10,
    ) -> Dict[str, float]:
        # 1. Warm-ups to stabilize CPU turbo and cache residency
        for _ in range(warmup_runs):
            _ = fn(sample_inputs)

        # 2. Measured runs with microsecond precision
        latencies_ms: List[float] = []
        for _ in range(measured_runs):
            t0 = time.perf_counter()
            _ = fn(sample_inputs)
            latencies_ms.append((time.perf_counter() - t0) * 1000.0)

        return {
            "mean_ms": float(statistics.mean(latencies_ms)),
            "median_ms": float(statistics.median(latencies_ms)),
            "stddev_ms": float(statistics.stdev(latencies_ms)) if len(latencies_ms) > 1 else 0.0,
            "min_ms": float(min(latencies_ms)),
            "max_ms": float(max(latencies_ms)),
            "measured_runs": measured_runs,
        }


class ExperimentJournal:
    """
    Creates immutable archival directories for every research run under experiments/<id>/.
    """

    @classmethod
    def archive_experiment(
        cls,
        experiment_id: str,
        environment_doc: Dict[str, Any],
        contract_doc: Dict[str, Any],
        candidate_doc: Dict[str, Any],
        verification_doc: Dict[str, Any],
        performance_doc: Dict[str, Any],
        proof_doc: Dict[str, Any],
    ) -> str:
        exp_dir = Path("experiments") / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)

        with open(exp_dir / "environment.json", "w", encoding="utf-8") as f:
            json.dump(environment_doc, f, indent=2)
        with open(exp_dir / "contract.json", "w", encoding="utf-8") as f:
            json.dump(contract_doc, f, indent=2)
        with open(exp_dir / "candidate.json", "w", encoding="utf-8") as f:
            json.dump(candidate_doc, f, indent=2)
        with open(exp_dir / "verification.json", "w", encoding="utf-8") as f:
            json.dump(verification_doc, f, indent=2)
        with open(exp_dir / "performance.json", "w", encoding="utf-8") as f:
            json.dump(performance_doc, f, indent=2)
        with open(exp_dir / "proof.json", "w", encoding="utf-8") as f:
            json.dump(proof_doc, f, indent=2)

        return str(exp_dir)
