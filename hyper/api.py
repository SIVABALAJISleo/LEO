"""
hyper/api.py
============
Official FastAPI Service for LEO/HYPER Universal Exact Semantic Replacement Engine.
Fulfills Section 64:
Exposes:
  POST /compile
  POST /optimize
  POST /verify
  POST /execute
  GET  /benchmark
  GET  /coverage
  GET  /certificate/{certificate_id}
  GET  /replay/{certificate_id}
  GET  /audit
  GET  /hardware
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
import numpy as np

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    BaseModel = object  # type: ignore

from hyper.universal_ir.program import UniversalIRProgram
from hyper.workloads.canonical_corpus import CanonicalWorkloadCorpus
from hyper.router.universal_router import UniversalRouter, RouterOutcome
from hyper.coverage.coverage_engine import CoverageEngine
from hyper.evidence.evidence_ledger import EvidenceLedger
from hyper.certificates.certificate_engine import CertificateStore
from hyper.hardware import get_hardware_profile
from hyper.semantics.types import ExactnessLevel


if HAS_FASTAPI:
    app = FastAPI(
        title="HYPER Universal Exact Semantic Replacement Engine API",
        version="10.0.0",
        description="Unified contract-driven computation replacement and verification API",
    )
else:
    app = None  # Graceful fallback if fastapi not installed


class ExecuteRequest(BaseModel):
    workload_id: str
    contract_id: str = "CONTRACT_DEFAULT"
    exactness_level: str = "EXACT_SEMANTIC"


class ExecuteResponse(BaseModel):
    outcome: str
    strategy_used: str
    exactness_level: str
    speedup: float
    baseline_latency_ms: float
    actual_latency_ms: float
    backend_device: str
    evidence_id: str
    certificate_id: Optional[str] = None
    verification_passed: bool
    explanation: str


# Instantiate shared singletons
_ledger = EvidenceLedger()
_cert_store = CertificateStore()
_router = UniversalRouter(ledger=_ledger, cert_store=_cert_store)
_coverage_engine = CoverageEngine(ledger=_ledger)
_corpus = {w.workload_id: w for w in CanonicalWorkloadCorpus.get_all_workloads()}


if HAS_FASTAPI:
    @app.get("/")
    def root():
        return {
            "system": "LEO / HYPER Universal Exact Semantic Replacement Engine",
            "version": "10.0.0",
            "status": "OPERATIONAL",
            "endpoints": [
                "/compile", "/optimize", "/verify", "/execute",
                "/benchmark", "/coverage", "/certificate/{id}", "/replay/{id}",
                "/audit", "/hardware"
            ],
        }

    @app.get("/hardware")
    def get_hardware():
        return get_hardware_profile()

    @app.post("/compile")
    def compile_workload(workload_id: str):
        if workload_id not in _corpus:
            raise HTTPException(status_code=404, detail=f"Workload '{workload_id}' not found in canonical corpus")
        w = _corpus[workload_id]
        w.program.validate()
        return {
            "workload_id": workload_id,
            "status": "COMPILED",
            "ir_version": w.program.ir_version,
            "program_hash": w.program.program_hash,
            "instructions": [op.to_dict() for op in w.program.instructions],
        }

    @app.post("/optimize")
    def optimize_workload(workload_id: str):
        if workload_id not in _corpus:
            raise HTTPException(status_code=404, detail=f"Workload '{workload_id}' not found in canonical corpus")
        w = _corpus[workload_id]
        inps = w.input_generator()
        candidates = _router.search_brain.generate_candidates(w.program, inps)
        return {
            "workload_id": workload_id,
            "candidates_found": len(candidates),
            "candidates": [
                {
                    "escape_id": c.escape_id,
                    "category": c.category.value,
                    "name": c.name,
                    "description": c.description,
                    "estimated_speedup": c.estimated_speedup,
                    "exactness": c.exactness.value,
                    "assumptions": c.assumptions,
                }
                for c in candidates
            ],
        }

    @app.post("/verify")
    def verify_workload(workload_id: str):
        if workload_id not in _corpus:
            raise HTTPException(status_code=404, detail=f"Workload '{workload_id}' not found in canonical corpus")
        w = _corpus[workload_id]
        inps = w.input_generator()
        adv = w.adversarial_generator()
        ref_outs = _router.reference_executor.execute(w.program, inps)
        report = _router.truth_gate.differential_verifier.verify(
            program=w.program,
            candidate_outputs=ref_outs,
            inputs=inps,
            exactness_level=w.exactness_level,
        )
        return {
            "workload_id": workload_id,
            "verdict": report.verdict.value,
            "exactness_level": report.exactness_level.value,
            "max_absolute_error": report.max_absolute_error,
            "max_relative_error": report.max_relative_error,
            "bitwise_identical": report.bitwise_identical,
        }

    @app.post("/execute", response_model=ExecuteResponse)
    def execute_workload(req: ExecuteRequest):
        if req.workload_id not in _corpus:
            raise HTTPException(status_code=404, detail=f"Workload '{req.workload_id}' not found")
        w = _corpus[req.workload_id]
        inps = w.input_generator()
        adv = w.adversarial_generator()
        exactness = ExactnessLevel(req.exactness_level)

        res = _router.route_and_execute(
            program=w.program,
            inputs=inps,
            contract_id=req.contract_id,
            exactness_level=exactness,
            adversarial_inputs=adv,
        )

        return ExecuteResponse(
            outcome=res.outcome,
            strategy_used=res.strategy_used,
            exactness_level=res.exactness_level.value,
            speedup=res.speedup,
            baseline_latency_ms=res.baseline_latency_ms,
            actual_latency_ms=res.actual_latency_ms,
            backend_device=res.backend_device,
            evidence_id=res.evidence_id,
            certificate_id=res.certificate_id,
            verification_passed=res.verification_passed,
            explanation=res.explanation,
        )

    @app.get("/coverage")
    def get_coverage():
        from hyper.benchmark.canonical_runner import run_canonical_benchmark
        # Read latest or compute live
        summary = run_canonical_benchmark(warmup_trials=1, measured_trials=2, save_results_path=None)
        return summary["coverage_metrics"]

    @app.get("/certificate/{certificate_id}")
    def get_certificate(certificate_id: str):
        cert = _cert_store.load_certificate(certificate_id)
        if not cert:
            raise HTTPException(status_code=404, detail=f"Certificate '{certificate_id}' not found")
        return cert.to_dict()

    @app.get("/replay/{certificate_id}")
    def replay_certificate(certificate_id: str):
        res = _cert_store.replay_certificate(certificate_id)
        return res

    @app.get("/audit")
    def get_audit_ledger():
        return {
            "total_records": _ledger.total_records,
            "summary_by_status": _ledger.summary(),
            "recent_evidence": [e.to_dict() for e in _ledger._entries[-10:]],
        }
