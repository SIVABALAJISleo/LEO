"""
hyper_x/leaf/telemetry/provenance.py
====================================
Provenance Classification for LEAF Execution Telemetry.

Mandate (Phase 46):
    Every result must carry one of:
    - MEASURED
    - DERIVED
    - ESTIMATED
    - SIMULATED
    - CACHED
    - PREDICTIVE
    - APPROXIMATE
    - UNKNOWN
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class ProvenanceClass(str, Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    ESTIMATED = "ESTIMATED"
    SIMULATED = "SIMULATED"
    CACHED = "CACHED"
    PREDICTIVE = "PREDICTIVE"
    APPROXIMATE = "APPROXIMATE"
    UNKNOWN = "UNKNOWN"
