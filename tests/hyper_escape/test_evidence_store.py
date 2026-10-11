"""
tests/hyper_escape/test_evidence_store.py
Validates Self-Improving Pathway Database & Evidence Store (Feature M / Section 15).
Tests persistence, record querying, summary scorecards, and historical evidence retention.
"""
import os
import tempfile
import pytest

from hyper_universal.evidence_store.database import PathwayEvidenceStore, PathwayRecord


def test_evidence_store_record_and_summary():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        tmp_db = f.name

    try:
        store = PathwayEvidenceStore(db_path=tmp_db)

        # Store 2 records: 1 exact verified, 1 failed correctness
        rec1 = PathwayRecord(
            workload_id="gemm_test",
            contract_version="1.0.0",
            candidate_id="cand_blocked",
            algorithm_family="CACHE_BLOCKING",
            backend="CPU_AVX2",
            verification_status="EXACT_VERIFIED",
            speedup=1.45,
            measured_latency_ms=10.2,
            peak_memory_mb=12.0,
        )
        rec2 = PathwayRecord(
            workload_id="gemm_test",
            contract_version="1.0.0",
            candidate_id="cand_broken",
            algorithm_family="AGGRESSIVE_PRUNE",
            backend="CPU_AVX2",
            verification_status="FAILED_CORRECTNESS",
            speedup=0.0,
            measured_latency_ms=0.0,
            failure_reason="Relative error exceeded tolerance",
        )

        store.record_candidate(rec1)
        store.record_candidate(rec2)

        # Verify summary statistics
        summary = store.summary()
        assert summary["total_records"] == 2
        assert summary["exact_verified_count"] == 1
        assert summary["failed_correctness_count"] == 1
        assert summary["contract_parity_percentage"] == 50.0

        # Query by workload
        workload_recs = store.get_by_workload("gemm_test")
        assert len(workload_recs) == 2

        # Reload store from disk
        store2 = PathwayEvidenceStore(db_path=tmp_db)
        assert len(store2.list_all()) == 2
    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
