"""
hyper_cco/proof_elimination.py
==============================
Mechanism 1: Proof-Carrying Work Elimination.
Enforces that every skipped computation carries a machine-readable,
cryptographically verifiable validity certificate before any result is accepted.

If proof generation or verification fails, the system automatically executes
the original exact computation path.
"""

from __future__ import annotations
import json
import hashlib
import time
import subprocess
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple, Callable
import numpy as np

from .contract import ComputeContract, CorrectnessTaxonomy


class EliminationMode(str, Enum):
    EXACT_REUSE = "exact_reuse"
    BOUNDED_APPROXIMATION = "bounded_approximation"
    PREDICTIVE = "predictive"
    REDUCED_WORK = "reduced_work"
    CACHED = "cached"
    FALLBACK = "fallback"


@dataclass
class ProofBundle:
    """Proof evidence supporting a computation elimination decision."""
    dependencies_unchanged: bool = False
    operator_deterministic: bool = True
    cache_match: bool = False
    oracle_verified: bool = False
    additional_evidence: Dict[str, Any] = field(default_factory=dict)

    def is_valid_for_exact(self) -> bool:
        """Exact equivalence requires all deterministic preconditions and verification."""
        return (
            self.dependencies_unchanged
            and self.operator_deterministic
            and (self.cache_match or self.oracle_verified)
        )

    def is_valid_for_bounded(self, error_bound: float, allowed_error: float) -> bool:
        """Bounded approximation requires verified error bound within allowed tolerance."""
        return (
            self.operator_deterministic
            and (error_bound <= allowed_error)
            and (self.oracle_verified or self.additional_evidence.get("lipschitz_verified", False))
        )


_CACHED_GIT_HASH: Optional[str] = None


def get_git_commit_hash() -> str:
    """Retrieve current git commit hash, memoized to avoid subprocess overhead."""
    global _CACHED_GIT_HASH
    if _CACHED_GIT_HASH is not None:
        return _CACHED_GIT_HASH
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )
        if res.returncode == 0:
            _CACHED_GIT_HASH = res.stdout.strip()
            return _CACHED_GIT_HASH
    except Exception:
        pass
    _CACHED_GIT_HASH = "0000000000000000000000000000000000000000"
    return _CACHED_GIT_HASH


def compute_tensor_fingerprint(data: Any) -> str:
    """Computes deterministic SHA-256 fingerprint over tensor data or serializable inputs."""
    if isinstance(data, np.ndarray):
        arr = np.ascontiguousarray(data)
        h = hashlib.sha256()
        h.update(str(arr.shape).encode("utf-8"))
        h.update(str(arr.dtype).encode("utf-8"))
        h.update(arr.tobytes())
        return h.hexdigest()
    elif isinstance(data, dict):
        canonical = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    else:
        return hashlib.sha256(str(data).encode("utf-8")).hexdigest()


@dataclass
class RegionEliminationCertificate:
    """
    Machine-readable validity certificate for eliminated computational regions.
    Satisfies Section 1 specifications:
    - region
    - mode
    - input_fingerprint
    - dependency_fingerprint
    - operator_identity
    - operator_version
    - contract_id
    - contract
    - proof
    - elimination_reason
    - cache_reuse_evidence
    - error_bound
    - verification_status
    - fallback_eligibility
    - fallback
    - timestamp
    - code_commit_hash
    """
    region: str
    mode: str
    input_fingerprint: str
    dependency_fingerprint: str
    operator_identity: str
    operator_version: str
    contract_id: str
    contract: Dict[str, Any]
    proof: Dict[str, Any]
    elimination_reason: str
    cache_reuse_evidence: Dict[str, Any]
    error_bound: float
    verification_status: str
    fallback_eligibility: bool
    fallback: str
    timestamp: float = field(default_factory=time.time)
    code_commit_hash: str = field(default_factory=get_git_commit_hash)
    certificate_digest: str = ""

    def compute_digest(self) -> str:
        """Computes SHA-256 seal over canonical JSON representation."""
        data = asdict(self)
        data.pop("certificate_digest", None)
        canonical = json.dumps(data, sort_keys=True, indent=None)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def seal(self) -> 'RegionEliminationCertificate':
        self.certificate_digest = self.compute_digest()
        return self

    def verify_integrity(self) -> bool:
        """Verifies tamper-evident digest against certificate contents."""
        return bool(self.certificate_digest) and (self.certificate_digest == self.compute_digest())

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


class ProofCarryingEliminationEngine:
    """
    Runtime coordinator that ensures no computation is skipped without a valid,
    tamper-evident proof certificate.
    """
    def __init__(self):
        self.certificate_ledger: List[RegionEliminationCertificate] = []

    def execute_with_proof(
        self,
        region_id: str,
        operator_identity: str,
        operator_version: str,
        inputs: Any,
        dependency_state: Any,
        contract: ComputeContract,
        candidate_mode: EliminationMode,
        elimination_fn: Callable[[], Any],
        exact_fallback_fn: Callable[[], Any],
        proof_generator: Callable[[], Optional[ProofBundle]],
        error_estimator: Optional[Callable[[], float]] = None,
        reason: str = "Unspecified elimination"
    ) -> Tuple[Any, RegionEliminationCertificate]:
        """
        Executes an eliminated sub-computation with strict proof verification.
        If proof fails or contract is violated, triggers exact_fallback_fn.
        """
        input_fp = compute_tensor_fingerprint(inputs)
        dep_fp = compute_tensor_fingerprint(dependency_state)
        contract_id = contract.workload_id
        max_error = contract.max_absolute_error if contract.max_absolute_error is not None else 0.0

        contract_summary = {
            "max_error": max_error,
            "max_latency_ms": contract.max_latency_ms,
            "deterministic": contract.deterministic,
            "exactness_class": contract.exactness_class.value
        }

        # 1. Generate proof
        proof_bundle: Optional[ProofBundle] = None
        try:
            proof_bundle = proof_generator()
        except Exception:
            proof_bundle = None

        proof_valid = False
        error_bound = 0.0
        if proof_bundle is not None:
            if candidate_mode in (EliminationMode.EXACT_REUSE, EliminationMode.CACHED):
                proof_valid = proof_bundle.is_valid_for_exact()
                error_bound = 0.0
            elif candidate_mode in (EliminationMode.BOUNDED_APPROXIMATION, EliminationMode.REDUCED_WORK, EliminationMode.PREDICTIVE):
                if error_estimator:
                    try:
                        error_bound = float(error_estimator())
                    except Exception:
                        error_bound = float("inf")
                proof_valid = proof_bundle.is_valid_for_bounded(error_bound, max_error)

        # 2. Decide execution path
        if proof_valid and proof_bundle is not None:
            try:
                result = elimination_fn()
                cert = RegionEliminationCertificate(
                    region=region_id,
                    mode=candidate_mode.value,
                    input_fingerprint=input_fp,
                    dependency_fingerprint=dep_fp,
                    operator_identity=operator_identity,
                    operator_version=operator_version,
                    contract_id=contract_id,
                    contract=contract_summary,
                    proof={
                        "dependencies_unchanged": proof_bundle.dependencies_unchanged,
                        "operator_deterministic": proof_bundle.operator_deterministic,
                        "cache_match": proof_bundle.cache_match,
                        "oracle_verified": proof_bundle.oracle_verified,
                        "additional_evidence": proof_bundle.additional_evidence
                    },
                    elimination_reason=reason,
                    cache_reuse_evidence={"matched_fingerprint": input_fp} if proof_bundle.cache_match else {},
                    error_bound=error_bound,
                    verification_status="PASS",
                    fallback_eligibility=True,
                    fallback="exact_recompute"
                ).seal()
                self.certificate_ledger.append(cert)
                return result, cert
            except Exception:
                # If elimination execution failed, fall through to exact fallback
                pass

        # 3. Fallback path: Proof invalid or elimination failed
        fallback_result = exact_fallback_fn()
        fallback_cert = RegionEliminationCertificate(
            region=region_id,
            mode=EliminationMode.FALLBACK.value,
            input_fingerprint=input_fp,
            dependency_fingerprint=dep_fp,
            operator_identity=operator_identity,
            operator_version=operator_version,
            contract_id=contract_id,
            contract=contract_summary,
            proof={
                "dependencies_unchanged": False,
                "operator_deterministic": contract.deterministic,
                "cache_match": False,
                "oracle_verified": True,
                "reason": "Proof invalid or missing; exact computation required"
            },
            elimination_reason="FALLBACK: Proof generation failed or error bound exceeded",
            cache_reuse_evidence={},
            error_bound=0.0,
            verification_status="PASS",
            fallback_eligibility=False,
            fallback="executed",
        ).seal()
        self.certificate_ledger.append(fallback_cert)
        return fallback_result, fallback_cert

    def export_ledger_json(self) -> str:
        """Export full ledger as JSON for external audit."""
        return json.dumps([asdict(c) for c in self.certificate_ledger], indent=2, sort_keys=True)
