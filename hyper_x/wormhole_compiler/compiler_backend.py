"""
hyper_x/wormhole_compiler/compiler_backend.py
=============================================================================
HYPER-X Compiler Backend Architecture (Phase 16–18)
=============================================================================
Defines the base interface for hardware execution backends:
  - CPUBackend
  - IGPUBackend
  - HybridBackend
"""

from __future__ import annotations
import abc
import time
from typing import Dict, Any, Tuple, Optional
import numpy as np


class CompilerBackend(abc.ABC):
    """Abstract base class for Wormhole Compiler hardware backends."""

    @abc.abstractmethod
    def name(self) -> str:
        """Name of the hardware backend."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Returns True if the underlying hardware/API runtime is operational."""
        pass

    @abc.abstractmethod
    def execute_matrix_multiply(
        self,
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[np.ndarray, float]:
        """
        Executes GEMM returning (result_tensor, elapsed_wall_clock_ms).
        """
        pass
