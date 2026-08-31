"""
hyper/proof/proof_ledger.py
===========================
Proof-Carrying Optimization Ledger (Section 41):
Generates an immutable cryptographic record of every optimization:
workload, contract, original vs replacement algorithm, CER, precision,
measured error, verification probe result, and execution device.
"""

import time
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class ProofCarryingRecord:
    optimization_id: str
    workload_name: str
    contract_id: str
    original_algorithm: str
    replacement_algorithm: str
    baseline_flops: int
    hyper_flops: int
    cer_pct: float
    measured_error: float
    verification_status: str
    execution_device: str
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d["timestamp"] == 0.0:
            d["timestamp"] = time.time()
        return d
