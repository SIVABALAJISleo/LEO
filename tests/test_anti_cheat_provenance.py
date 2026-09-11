"""
tests/test_anti_cheat_provenance.py
===================================
Unit tests for Mechanism 7: Anti-Cheat Provenance Ledger.
"""

import pytest
from hyper_cco.provenance_ledger import (
    ProvenanceLedger,
    BenchmarkProvenanceRecord,
    TruthfulnessLabel
)


def test_provenance_record_completeness_and_seal():
    ledger = ProvenanceLedger()
    rec = ledger.create_record(
        workload_id="PROVENANCE_TEST",
        input_hash="hash_input_123",
        output_hash="hash_output_456",
        exact_baseline_latency_ms=10.5,
        optimized_latency_ms=3.2,
        error_metrics={"max_abs": 0.001},
        truthfulness_label=TruthfulnessLabel.MEASURED
    )

    assert rec.validate_completeness() is True
    assert rec.verify_seal() is True
    assert len(rec.provenance_hash) == 64
    assert rec.truthfulness_label == TruthfulnessLabel.MEASURED


def test_provenance_rejection_on_missing_fields():
    # Attempting to seal record with empty git commit or invalid field
    rec = BenchmarkProvenanceRecord(
        workload_id="INCOMPLETE_TEST",
        repository_commit="",  # Empty commit should fail validation
        module_version="v1.0",
        dataset_hash="hash1",
        input_hash="hash2",
        output_hash="hash3",
        model_hash="hash4",
        compiler_version="clang",
        compiler_flags="-O3",
        runtime_version="py313",
        driver_version="drv1",
        os_version="win11",
        hardware_identity="i5",
        cpu_affinity="p-cores",
        igpu_device="uhd",
        cache_state="warm",
        warmup_count=5,
        number_of_repetitions=10,
        thermal_state={},
        power_state={},
        fallback_count=0,
        verification_count=10,
        exact_baseline_latency_ms=1.0,
        optimized_latency_ms=0.5,
        error_metrics={},
        confidence_interval=(0.9, 0.99),
        failure_count=0,
        truthfulness_label=TruthfulnessLabel.MEASURED
    )

    assert rec.validate_completeness() is False
    with pytest.raises(ValueError):
        rec.seal()
