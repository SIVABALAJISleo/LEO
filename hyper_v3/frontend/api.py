"""
hyper_v3/frontend/api.py
Frontend entry API for contract parsing and workload initialization.
"""

from typing import Dict, Any, Optional
from hyper_v3.frontend.contract_parser import ContractParser, ExecutionContract, ExecutionTrack
from hyper_v3.frontend.program_observer import ProgramObserver
from hyper_v3.frontend.workload_loader import WorkloadLoader


class FrontendAPI:
    """Provides high-level frontend interfaces for HYPER 3.0."""

    @staticmethod
    def initialize_contract(workload_name: str, track: str = "exact", custom_params: Optional[Dict[str, Any]] = None) -> ExecutionContract:
        if track == "contract_aware" or track == "track_b_contract_aware":
            params = custom_params or {}
            return ContractParser.create_contract_aware_contract(workload_name, **params)
        return ContractParser.create_exact_contract(workload_name)

    @staticmethod
    def inspect(workload_name: str, sample_inputs: Dict[str, Any]) -> Dict[str, Any]:
        return ProgramObserver.profile_workload(workload_name, sample_inputs)
