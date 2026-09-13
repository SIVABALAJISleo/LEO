#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/decp/manifest.py
========================
Phase 7: Frozen Execution Manifest for Deterministic Exact-Compute.
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional


@dataclass
class FrozenExecutionManifest:
    workload_id: str
    precision: str = "FP32"
    accumulator_precision: str = "FP32"
    random_seed: int = 42
    thread_count: int = 8
    reduction_ordering: str = "CANONICAL_TREE"
    denormal_policy: str = "FTZ_DAZ_EXPLICIT"
    quantization_scheme: Optional[str] = None
    model_hash: Optional[str] = None
    compiler_version: str = "vNext-1.0"
    runtime_environment: str = "Intel Core i5-12450H + UHD Graphics (48 EU)"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compute_manifest_hash(self) -> str:
        serialized = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
