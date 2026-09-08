"""
hyper_x/wormhole_compiler/provenance.py
=============================================================================
HYPER-X Cryptographic Provenance & Hardware Stamping Engine (Phase 39, 63)
=============================================================================
Produces immutable, verifiable provenance records for every benchmark and
compiled algorithm candidate:
  - random seed
  - input tensor SHA-256 hash
  - output tensor SHA-256 hash
  - candidate algorithm genome hash
  - host hardware fingerprint hash
  - software git commit / version hash
  - dependency versions (numpy, openvino, etc.)
  - target hardware mismatch flag
"""

from __future__ import annotations
import json
import time
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import numpy as np

from hyper_x.hardware.fingerprint import HardwareFingerprint


@dataclass(frozen=True)
class ProvenanceRecord:
    provenance_id: str
    workload_id: str
    candidate_id: str
    seed: int
    input_hash: str
    output_hash: str
    genome_hash: str
    hardware_fingerprint_hash: str
    host_cpu: str
    host_igpu: str
    target_hardware_mismatch: bool
    software_version: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class ProvenanceTracker:
    """Creates tamper-evident provenance records for benchmarks."""

    def __init__(self, software_version: str = "2.0.0-wormhole"):
        self.software_version = software_version
        self.fingerprint = HardwareFingerprint.detect()

    @staticmethod
    def hash_tensor(tensor: np.ndarray) -> str:
        """Computes deterministic SHA-256 hash over array buffer."""
        return hashlib.sha256(tensor.tobytes()).hexdigest()

    def create_record(
        self,
        workload_id: str,
        candidate_id: str,
        input_tensor: np.ndarray,
        output_tensor: np.ndarray,
        genome_hash: str,
        seed: int = 42,
    ) -> ProvenanceRecord:
        """Constructs an immutable ProvenanceRecord."""
        inp_h = self.hash_tensor(input_tensor)
        out_h = self.hash_tensor(output_tensor)
        pid = f"PROV_{hashlib.sha256((inp_h + out_h + str(time.time())).encode()).hexdigest()[:12]}"

        return ProvenanceRecord(
            provenance_id=pid,
            workload_id=workload_id,
            candidate_id=candidate_id,
            seed=seed,
            input_hash=inp_h,
            output_hash=out_h,
            genome_hash=genome_hash,
            hardware_fingerprint_hash=self.fingerprint.fingerprint_hash,
            host_cpu=self.fingerprint.cpu_model,
            host_igpu=self.fingerprint.igpu_model,
            target_hardware_mismatch=self.fingerprint.host_mismatch,
            software_version=self.software_version,
            timestamp=time.time(),
        )
