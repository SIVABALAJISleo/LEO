"""
hyper_omega/adapters/base.py
Universal Workload Adapter Base Class (Prompt Section 30).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_omega.contracts.models import WorkloadContract
from hyper_omega.structure.detectors import StructuralAnalysisResult, StructuralEscapeDetector


class WorkloadAdapter(ABC):
    """Abstract interface for domain-specific workload adapters."""

    @abstractmethod
    def supports(self, workload_name: str, contract: WorkloadContract) -> bool:
        """Returns True if this adapter can process the given workload."""
        pass

    @abstractmethod
    def canonical_reference(self, input_data: Any) -> Any:
        """Executes the standard, unoptimized baseline reference."""
        pass

    @abstractmethod
    def discover_and_prove(
        self, input_data: Any, contract: WorkloadContract
    ) -> Tuple[bool, Optional[Callable[[Any], Any]], str, Dict[str, Any]]:
        """
        Discovers a cheaper computational escape and formal proof.
        Returns: (is_proven, candidate_kernel, proof_statement, metadata)
        """
        pass
