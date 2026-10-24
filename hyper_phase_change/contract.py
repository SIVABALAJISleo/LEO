"""
hyper_phase_change/contract.py
==============================
Authoritative Workload Contract System for the Universal Replacement Fabric.

Defines:
1. Exactness classes: BIT_EXACT, INTEGER_EXACT, NUMERICALLY_EQUIVALENT, SEMANTICALLY_EQUIVALENT.
2. TensorSchema with shape, dtype, range, and non-finite value constraints.
3. WorkloadContract governing execution semantics, tolerances, and verification checks.
4. Complete 15/15 canonical workload contract definitions.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# Integrate seamlessly with hyper.canonical authoritative registry
from hyper.canonical.workload_registry import (
    ExactnessClass,
    TensorSchema,
    CanonicalWorkloadContract as WorkloadContract,
    CanonicalWorkloadRegistry as WorkloadContractRegistry,
    CANONICAL_REGISTRY,
    CANONICAL_15_WORKLOAD_IDS,
)

__all__ = [
    "ExactnessClass",
    "TensorSchema",
    "WorkloadContract",
    "WorkloadContractRegistry",
    "CANONICAL_REGISTRY",
    "CANONICAL_15_WORKLOAD_IDS",
]
