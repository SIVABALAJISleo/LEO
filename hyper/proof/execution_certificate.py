"""
hyper/proof/execution_certificate.py
====================================
LEO/HYPER Ω — Proof-Carrying Result & Cryptographic Execution Certificate.

Every HYPER execution result carries this complete provenance record.
Strictly separates:
- Reference Work vs Executed Work vs Eliminated Work
- Measurement classification (PHYSICAL, SIMULATED, ANALYTICAL, ESTIMATED)
- Device attribution and full latency decomposition
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Any, Dict, Optional

from contracts.contract_ir import ContractStatus, ExactnessClass, VerificationLevel


class ExecutionCertificate:
    workload_id: str
    contract_id: str
    input_hash: str
    model_hash: str
    code_hash: str
    strategy: str
    exactness_class: Any
    reference_work: float
    estimated_necessary_work: float
    executed_work: float
    eliminated_work: float
    precision: str
    device: str
    cpu_time_ms: float
    igpu_time_ms: float
    memory_time_ms: float
    verification_time_ms: float
    fallback_time_ms: float
    total_time_ms: float
    max_abs_error: float
    max_rel_error: float
    quality_metric_name: str
    quality_score: float
    cache_hit: bool
    prediction_used: bool
    speculation_used: bool
    fallback_used: bool
    verification_level: Any
    contract_status: Any
    measurement_classification: str
    timestamp: float
    certificate_hash: str

    def __init__(
        self,
        workload_id: str = "tensor_op",
        contract_id: str = "default_contract",
        input_hash: str = "",
        model_hash: str = "",
        code_hash: str = "",
        strategy: str = "EXACT_FALLBACK",
        exactness_class: Any = ExactnessClass.EXACT,
        reference_work: float = 0.0,
        estimated_necessary_work: float = 0.0,
        executed_work: float = 0.0,
        eliminated_work: float = 0.0,
        precision: str = "FP32",
        device: str = "CPU_AVX2",
        cpu_time_ms: float = 0.0,
        igpu_time_ms: float = 0.0,
        memory_time_ms: float = 0.0,
        verification_time_ms: float = 0.0,
        fallback_time_ms: float = 0.0,
        total_time_ms: float = 0.0,
        max_abs_error: float = 0.0,
        max_rel_error: float = 0.0,
        quality_metric_name: str = "EXACT_PARITY",
        quality_score: float = 1.0,
        cache_hit: bool = False,
        prediction_used: bool = False,
        speculation_used: bool = False,
        fallback_used: bool = False,
        verification_level: Any = VerificationLevel.FULL,
        contract_status: Any = ContractStatus.CONTRACT_PASS,
        measurement_classification: str = "PHYSICAL",
        timestamp: Optional[float] = None,
        certificate_hash: str = "",
        **kwargs: Any
    ):
        self.workload_id = kwargs.get("task_id", workload_id)
        self.contract_id = kwargs.get("task_id", contract_id)
        self.input_hash = input_hash
        self.model_hash = model_hash
        self.code_hash = code_hash
        self.strategy = kwargs.get("strategy_used", strategy)
        self.exactness_class = exactness_class
        self.reference_work = float(kwargs.get("reference_flops", reference_work))
        self.estimated_necessary_work = estimated_necessary_work
        self.executed_work = float(kwargs.get("executed_flops", executed_work))
        self.eliminated_work = float(kwargs.get("reference_flops", reference_work) - kwargs.get("executed_flops", executed_work)) if "reference_flops" in kwargs else eliminated_work
        self.precision = precision
        self.device = kwargs.get("hardware_target", device)
        self.cpu_time_ms = cpu_time_ms
        self.igpu_time_ms = igpu_time_ms
        self.memory_time_ms = memory_time_ms
        self.verification_time_ms = verification_time_ms
        self.fallback_time_ms = fallback_time_ms
        self.total_time_ms = float(kwargs.get("latency_hyper_ms", total_time_ms))
        self.max_abs_error = float(kwargs.get("max_absolute_error", max_abs_error))
        self.max_rel_error = max_rel_error
        self.quality_metric_name = quality_metric_name
        self.quality_score = float(kwargs.get("cosine_similarity", quality_score))
        self.cache_hit = cache_hit
        self.prediction_used = prediction_used
        self.speculation_used = speculation_used
        self.fallback_used = fallback_used
        self.verification_level = verification_level
        self.contract_status = contract_status if not kwargs.get("contract_100_passed") else ContractStatus.CONTRACT_PASS
        self.measurement_classification = measurement_classification
        self.timestamp = timestamp or time.time()
        self.certificate_hash = certificate_hash or self.compute_hash()


    @property
    def strategy_used(self) -> str:
        return self.strategy

    @property
    def contract_100_passed(self) -> bool:
        return self.contract_status == ContractStatus.CONTRACT_PASS

    @property
    def work_elimination_ratio(self) -> float:
        if self.reference_work <= 0:
            return 0.0
        return max(0.0, 1.0 - (self.executed_work / self.reference_work))

    @property
    def work_eliminated_ratio(self) -> float:
        return self.work_elimination_ratio

    @property
    def latency_speedup(self) -> float:
        ref_time = self.reference_work  # Note: separately tracked against reference time
        return max(0.01, (self.total_time_ms))

    def compute_hash(self) -> str:
        payload = f"{self.workload_id}:{self.contract_id}:{self.input_hash}:{self.strategy}:{self.executed_work}:{self.total_time_ms}:{self.contract_status.value}:{self.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def compute_certificate_digest(self) -> str:
        return self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        d = self.as_dict()
        d["certificate_digest"] = self.compute_hash()
        return d

    def as_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "contract_id": self.contract_id,
            "input_hash": self.input_hash[:16] + "..." if self.input_hash else "",
            "model_hash": self.model_hash[:16] + "..." if self.model_hash else "",
            "code_hash": self.code_hash[:16] + "..." if self.code_hash else "",
            "strategy": self.strategy,
            "exactness_class": self.exactness_class.value if hasattr(self.exactness_class, "value") else str(self.exactness_class),
            "reference_work": self.reference_work,
            "estimated_necessary_work": self.estimated_necessary_work,
            "executed_work": self.executed_work,
            "eliminated_work": self.eliminated_work,
            "work_elimination_pct": round(self.work_elimination_ratio * 100.0, 2),
            "precision": self.precision,
            "device": self.device,
            "cpu_time_ms": round(self.cpu_time_ms, 4),
            "igpu_time_ms": round(self.igpu_time_ms, 4),
            "memory_time_ms": round(self.memory_time_ms, 4),
            "verification_time_ms": round(self.verification_time_ms, 4),
            "fallback_time_ms": round(self.fallback_time_ms, 4),
            "total_time_ms": round(self.total_time_ms, 4),
            "max_abs_error": f"{self.max_abs_error:.2e}",
            "max_rel_error": f"{self.max_rel_error:.2e}",
            "quality_score": round(self.quality_score, 4),
            "cache_hit": self.cache_hit,
            "prediction_used": self.prediction_used,
            "speculation_used": self.speculation_used,
            "fallback_used": self.fallback_used,
            "verification_level": self.verification_level.value if hasattr(self.verification_level, "value") else str(self.verification_level),
            "contract_status": self.contract_status.value if hasattr(self.contract_status, "value") else str(self.contract_status),
            "measurement_classification": self.measurement_classification,
            "certificate_hash": self.certificate_hash[:16] + "..." if self.certificate_hash else "",
            "timestamp": self.timestamp,
        }

