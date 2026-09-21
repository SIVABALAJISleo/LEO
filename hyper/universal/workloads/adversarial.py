"""
hyper/universal/workloads/adversarial.py
=======================================
Section 41: Adversarial Workload Testing.
Generates pathological, dense, irregular, and worst-case stress workloads:
- Maximally incompressible white noise (entropy barrier)
- Serial recurrence chain (dependency barrier)
- Ill-conditioned Hilbert matrices (precision barrier)
- Worst-case reverse-ordered sorting inputs
"""

from __future__ import annotations

import numpy as np
from typing import Any, Callable, Dict, Tuple

from ..adapter.workload_adapter import UniversalWorkload, UniversalWorkloadAdapter
from ..adapter.workload_types import WorkloadDomain
from ..contracts.universal_contract import UniversalContract, ContractCorrectness, PrecisionTier


class AdversarialWorkloadGenerator:
    """Generates adversarial workloads designed to stress the engine."""

    @staticmethod
    def get_incompressible_noise_workload(size: int = 10000) -> Tuple[UniversalWorkload, UniversalContract]:
        """High-entropy uniform random bytes designed to hit the Information Entropy Barrier."""
        rng = np.random.default_rng(999)
        noise = rng.integers(0, 256, size=size, dtype=np.uint8)

        def identity_eval(x: np.ndarray) -> np.ndarray:
            return x.copy()

        wl = UniversalWorkloadAdapter.adapt(
            target=identity_eval,
            sample_input=noise,
            workload_id="adv_incompressible_noise",
            domain=WorkloadDomain.CRYPTOGRAPHIC,
            name="Incompressible High-Entropy Uniform Noise",
        )

        c = UniversalContract(
            contract_id="contract_adv_noise",
            workload_id=wl.workload_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.INT8,
            numeric_tolerance=0.0,
            verification_method="EXACT",
        )
        return wl, c

    @staticmethod
    def get_serial_recurrence_workload(steps: int = 1000) -> Tuple[UniversalWorkload, UniversalContract]:
        """Strict loop-carried recurrence designed to test the Dependency Barrier."""
        seed_val = np.float32(0.5)

        def serial_chain(x0: np.float32) -> np.float32:
            val = x0
            for _ in range(steps):
                val = np.sin(val) * 0.99
            return val

        wl = UniversalWorkloadAdapter.adapt(
            target=serial_chain,
            sample_input=seed_val,
            workload_id="adv_serial_recurrence",
            domain=WorkloadDomain.SCIENTIFIC_SIMULATION,
            name="Strict Loop-Carried Serial Recurrence",
        )

        c = UniversalContract(
            contract_id="contract_adv_recurrence",
            workload_id=wl.workload_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.FLOAT32,
            numeric_tolerance=1e-5,
            verification_method="DIFFERENTIAL",
        )
        return wl, c
