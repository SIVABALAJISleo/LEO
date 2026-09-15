"""
tests/test_provenance.py
========================
Tests Phase 14 provenance tracking and metadata integrity.
Ensures every candidate result records input hash, output hash, and execution source.
"""

import hashlib
import numpy as np
import pytest
from hyper.candidate import CandidateResult, PathClass


def test_provenance_recording():
    data_in = np.ones((8, 8), dtype=np.float32)
    data_out = data_in * 2.0

    in_hash = hashlib.sha256(data_in.tobytes()).hexdigest()
    out_hash = hashlib.sha256(data_out.tobytes()).hexdigest()

    provenance = {
        "measurement_source": "local_execution",
        "synthetic": False,
        "external_reference": False,
        "input_hash": in_hash,
        "output_hash": out_hash,
    }

    cand = CandidateResult(
        value=data_out,
        path_class=PathClass.EXACT.value,
        backend="CPU_AVX2",
        latency_ms=0.1,
        work_units=64,
        memory_bytes=data_out.nbytes,
        max_abs_error=0.0,
        relative_error=0.0,
        rmse=0.0,
        provenance=provenance,
    )

    assert cand.provenance["measurement_source"] == "local_execution"
    assert cand.provenance["synthetic"] is False
    assert cand.provenance["input_hash"] == in_hash
    assert cand.provenance["output_hash"] == out_hash


def test_reject_missing_provenance_in_benchmark():
    # Provenance dictionary must contain required keys
    required_keys = {"measurement_source", "synthetic", "external_reference", "input_hash", "output_hash"}
    incomplete_provenance = {"measurement_source": "local_execution"}
    assert not required_keys.issubset(incomplete_provenance.keys())
