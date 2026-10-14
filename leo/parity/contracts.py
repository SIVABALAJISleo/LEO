"""
leo/parity/contracts.py
=======================
Contract parsing, SHA-256 frozen hashing, and strict label verification.
"""

from __future__ import annotations
import enum
import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml


class ResultLabel(str, enum.Enum):
    """
    Every result carries EXACTLY one label. Never merge labels into one score.
    """
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    CACHED = "CACHED"
    PREDICTIVE = "PREDICTIVE"
    REDUCED_WORK = "REDUCED_WORK"
    EMULATED = "EMULATED"  # Emulation immediately FAILS the contract per Rule 1


@dataclass
class ExecutionResult:
    """
    Normalized result container for any executed computational pathway.
    """
    output: Any
    label: ResultLabel
    latency_ms: float
    peak_ram_mb: float
    correctness_metric_value: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False
    emulated: bool = False
    failure_reason: Optional[str] = None

    def enforce_rules(self, allowed_labels: Set[str]) -> bool:
        """
        Enforce Rule 1 & Rule 2:
        - If emulated, label MUST be EMULATED and contract verification FAILS.
        - Label must be strictly within contract's allowed_labels.
        """
        if self.emulated or self.label == ResultLabel.EMULATED:
            self.label = ResultLabel.EMULATED
            self.verified = False
            self.failure_reason = "Rule 1 Violation: Emulated result detected; contract failed."
            return False

        if self.label.value not in allowed_labels:
            self.verified = False
            self.failure_reason = f"Rule 2 Violation: Label {self.label.value} not permitted by contract ({allowed_labels})."
            return False

        return self.verified


@dataclass
class ContractDef:
    """
    Immutable workload contract definition loaded from contracts.yaml.
    """
    workload_id: str
    description: str
    input_spec: Dict[str, Any]
    reference_implementation: str
    candidate_implementation: str
    correctness_metric: str
    quality_threshold: float
    max_relative_error: float
    latency_cap_ms: float
    peak_ram_cap_mb: float
    allowed_labels: Set[str]
    cold_run_required: bool = True

    def validate_execution(self, result: ExecutionResult) -> bool:
        """
        Validates an execution result against all contract clauses:
        1. Emulation check (Rule 1).
        2. Single allowed label check (Rule 2).
        3. Correctness metric threshold.
        4. Latency ceiling.
        5. Peak RAM ceiling.
        """
        if not result.enforce_rules(self.allowed_labels):
            return False

        # Correctness metric validation
        if result.correctness_metric_value < self.quality_threshold:
            result.verified = False
            result.failure_reason = (
                f"Quality threshold failed: {result.correctness_metric_value:.4f} < {self.quality_threshold:.4f}"
            )
            return False

        # Latency cap validation
        if result.latency_ms > self.latency_cap_ms:
            result.verified = False
            result.failure_reason = (
                f"Latency cap exceeded: {result.latency_ms:.2f} ms > {self.latency_cap_ms:.2f} ms"
            )
            return False

        # Peak RAM cap validation
        if result.peak_ram_mb > self.peak_ram_cap_mb:
            result.verified = False
            result.failure_reason = (
                f"Peak RAM cap exceeded: {result.peak_ram_mb:.2f} MB > {self.peak_ram_cap_mb:.2f} MB"
            )
            return False

        result.verified = True
        return True


@dataclass
class ContractsRegistry:
    version: str
    contracts_hash: str
    contracts_path: str
    contracts: Dict[str, ContractDef]

    def get_contract(self, name: str) -> ContractDef:
        if name not in self.contracts:
            raise KeyError(f"Contract '{name}' not found in registry (available: {list(self.contracts.keys())})")
        return self.contracts[name]


def compute_file_sha256(path: str | Path) -> str:
    """Computes SHA-256 digest of a file to freeze contract definitions."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_and_freeze_contracts(contracts_path: str = "contracts.yaml") -> ContractsRegistry:
    """
    Loads contracts.yaml and freezes its content by cryptographic SHA-256 hash.
    Rule 3: Contracts are written BEFORE benchmarking and frozen by hash.
    """
    if not os.path.exists(contracts_path):
        raise FileNotFoundError(f"Contracts file not found at: {contracts_path}")

    frozen_hash = compute_file_sha256(contracts_path)

    with open(contracts_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    version = raw.get("version", "1.0.0")
    contracts_raw = raw.get("contracts", {})

    parsed_contracts: Dict[str, ContractDef] = {}
    for name, c in contracts_raw.items():
        parsed_contracts[name] = ContractDef(
            workload_id=c["workload_id"],
            description=c.get("description", ""),
            input_spec=c.get("input_spec", {}),
            reference_implementation=c.get("reference_implementation", ""),
            candidate_implementation=c.get("candidate_implementation", ""),
            correctness_metric=c.get("correctness_metric", "exact_match"),
            quality_threshold=float(c.get("quality_threshold", 1.0)),
            max_relative_error=float(c.get("max_relative_error", 1e-4)),
            latency_cap_ms=float(c.get("latency_cap_ms", 100.0)),
            peak_ram_cap_mb=float(c.get("peak_ram_cap_mb", 64.0)),
            allowed_labels=set(c.get("allowed_labels", ["EXACT"])),
            cold_run_required=bool(c.get("cold_run_required", True)),
        )

    return ContractsRegistry(
        version=version,
        contracts_hash=frozen_hash,
        contracts_path=str(Path(contracts_path).resolve()),
        contracts=parsed_contracts,
    )
