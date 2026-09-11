"""
hyper/casa/__init__.py
======================
Contract-Aware Sieve Architecture (CASA) Integration Package.
Project LEO / HYPER.

Exports:
  - CASAOrchestrator: Unified master execution engine.
  - TMacLUTEngine: Phase 1 Arithmetic Dematerialization (T-MAC 1.58-bit LUT).
  - SpatioTemporalSieve: Phase 2 Anomaly-Driven Delta Sieve on E-cores.
  - ZeroCopyUSMManager, ZeroCopyUSMBuffer: Phase 3 Intel Level Zero USM PCIe bypass.
  - ComplexityInverter, StateSpaceModelEngine, SimHashLSHIndex: Phase 4 Complexity Inversion.
"""

from .tmac_lut_engine import TMacLUTEngine
from .spatio_temporal_sieve import SpatioTemporalSieve
from .zero_copy_usm import ZeroCopyUSMManager, ZeroCopyUSMBuffer
from .complexity_inversion import ComplexityInverter, StateSpaceModelEngine, SimHashLSHIndex
from .casa_orchestrator import CASAOrchestrator

__all__ = [
    "CASAOrchestrator",
    "TMacLUTEngine",
    "SpatioTemporalSieve",
    "ZeroCopyUSMManager",
    "ZeroCopyUSMBuffer",
    "ComplexityInverter",
    "StateSpaceModelEngine",
    "SimHashLSHIndex",
]
