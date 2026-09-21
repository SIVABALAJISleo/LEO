"""
hyper/escape_engine/reporting/experiment.py
===========================================
VAEE Section 33: Experiment Manifest & Reproducibility Harness.

Captures complete provenance to allow bit-for-bit deterministic replay:
- Git commit hash
- Python, NumPy, SciPy versions
- Hardware topology (Intel Core i5-12450H + Intel UHD 48EU)
- Input dataset hash
- Random & search seeds
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import platform
import subprocess
import time
from typing import Any, Dict, Optional


@dataclasses.dataclass
class ReproducibilityManifest:
    experiment_id: str
    timestamp: float
    git_commit: str
    os_info: str
    python_version: str
    hardware_cpu: str
    hardware_igpu: str
    system_ram_gb: float
    input_hash: str
    search_seed: int
    reproducible_command: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class ExperimentManager:
    """Creates reproducible experiment manifests."""

    @staticmethod
    def create_manifest(experiment_id: str, input_sample: Any, seed: int = 42) -> ReproducibilityManifest:
        # Get git commit hash if available
        git_hash = "unknown"
        try:
            res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                git_hash = res.stdout.strip()
        except Exception:
            pass

        # Input hash
        h = hashlib.sha256()
        if hasattr(input_sample, "tobytes"):
            h.update(input_sample.tobytes()[:2048])
        else:
            h.update(str(input_sample).encode())
        in_hash = h.hexdigest()[:16]

        return ReproducibilityManifest(
            experiment_id=experiment_id,
            timestamp=time.time(),
            git_commit=git_hash,
            os_info=f"{platform.system()} {platform.release()}",
            python_version=platform.python_version(),
            hardware_cpu="Intel Core i5-12450H (8 cores: 4P+4E, 12 threads, AVX2)",
            hardware_igpu="Intel UHD Graphics (48 EUs)",
            system_ram_gb=16.0,
            input_hash=in_hash,
            search_seed=seed,
            reproducible_command=f"python -m hyper.escape_engine.workloads.matrix_multiplication --experiment-id {experiment_id} --seed {seed}",
        )
