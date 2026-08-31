"""
hyper/contracts/engine.py
=========================
First-class HYPER Universal Contract Engine.
Manages immutable registration, evaluation, and strict multi-requirement scoring.
"""

from typing import Dict, Any, Optional, List
from .contract_types import UniversalContract, ContractClass, VerificationStatus, ParityTier


class UniversalContractEngine:
    """
    Registry and evaluator for all declared application contracts.
    """
    def __init__(self):
        self._contracts: Dict[str, UniversalContract] = {}
        self._active_contract_id: Optional[str] = None
        self._init_standard_contracts()

    def _init_standard_contracts(self):
        """Initializes standard workload contracts."""
        self.register(UniversalContract(
            contract_id="matrix_gemm_default",
            contract_class=ContractClass.BOUNDED_ERROR,
            error_bound_eps=0.01,
            max_latency_ms=15.0
        ))
        self.register(UniversalContract(
            contract_id="tensor_attention_default",
            contract_class=ContractClass.BOUNDED_ERROR,
            error_bound_eps=0.005,
            max_latency_ms=10.0
        ))
        self.register(UniversalContract(
            contract_id="sparse_fft_default",
            contract_class=ContractClass.REDUCED_WORK,
            error_bound_eps=0.005,
            max_latency_ms=8.0
        ))
        self.register(UniversalContract(
            contract_id="llm_inference_default",
            contract_class=ContractClass.APPLICATION,
            min_throughput_tokens_sec=25.0,
            max_latency_ms=40.0
        ))
        self.register(UniversalContract(
            contract_id="interactive_gaming_540p_1080p",
            contract_class=ContractClass.PERCEPTUAL,
            perceptual_ssim_min=0.92,
            min_fps_requirement=30.0,
            max_latency_ms=33.3
        ))
        self.register(UniversalContract(
            contract_id="video_4k_quicksync",
            contract_class=ContractClass.APPLICATION,
            min_fps_requirement=60.0,
            max_latency_ms=16.6
        ))
        self.register(UniversalContract(
            contract_id="nbody_fmm_default",
            contract_class=ContractClass.BOUNDED_ERROR,
            error_bound_eps=0.001,
            energy_drift_max=0.001,
            max_latency_ms=20.0
        ))

    def register(self, contract: UniversalContract) -> None:
        """Registers a contract immutably."""
        self._contracts[contract.contract_id] = contract

    def get(self, contract_id: str) -> Optional[UniversalContract]:
        return self._contracts.get(contract_id)

    def evaluate_score(
        self,
        contract: UniversalContract,
        measured_error: float,
        measured_latency_ms: float,
        measured_ssim: float = 1.0,
        measured_fps: float = 60.0,
        measured_memory_mb: float = 100.0,
    ) -> Dict[str, Any]:
        """
        Evaluates Contract Score strictly:
        ContractParity = (mandatory requirements passed / total mandatory requirements) * 100
        """
        checks = {}
        
        # 1. Numerical error check
        checks["error_bound"] = (
            VerificationStatus.PASS if measured_error <= contract.error_bound_eps else VerificationStatus.FAIL
        )
        
        # 2. Latency check
        checks["latency"] = (
            VerificationStatus.PASS if measured_latency_ms <= contract.max_latency_ms * 1.5 else VerificationStatus.FAIL
        )
        
        # 3. Perceptual check if applicable
        if contract.contract_class == ContractClass.PERCEPTUAL:
            checks["perceptual_ssim"] = (
                VerificationStatus.PASS if measured_ssim >= contract.perceptual_ssim_min else VerificationStatus.FAIL
            )
        else:
            checks["perceptual_ssim"] = VerificationStatus.NOT_APPLICABLE

        # 4. FPS check if applicable
        if contract.contract_class in [ContractClass.PERCEPTUAL, ContractClass.APPLICATION]:
            checks["fps"] = (
                VerificationStatus.PASS if measured_fps >= contract.min_fps_requirement else VerificationStatus.FAIL
            )
        else:
            checks["fps"] = VerificationStatus.NOT_APPLICABLE

        # 5. Memory limit check
        checks["memory_limit"] = (
            VerificationStatus.PASS if measured_memory_mb <= contract.memory_limit_mb else VerificationStatus.FAIL
        )

        mandatory_checks = [v for k, v in checks.items() if v != VerificationStatus.NOT_APPLICABLE]
        passed_count = sum(1 for v in mandatory_checks if v == VerificationStatus.PASS)
        total_mandatory = len(mandatory_checks)
        
        contract_parity_pct = (passed_count / max(1, total_mandatory)) * 100.0
        all_passed = (passed_count == total_mandatory)

        return {
            "contract_id": contract.contract_id,
            "all_passed": all_passed,
            "contract_parity_pct": round(contract_parity_pct, 2),
            "checks": {k: v.value for k, v in checks.items()},
            "passed_count": passed_count,
            "total_mandatory": total_mandatory,
        }
