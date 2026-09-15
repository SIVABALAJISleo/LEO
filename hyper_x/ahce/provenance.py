"""
hyper_x/ahce/provenance.py
==========================
Strict evidence provenance tracking for AHCE.

Every number, measurement, and verdict must carry an immutable provenance tag:
- MEASURED:   Directly recorded via physical timer or hardware performance counter.
- REFERENCE:  Obtained from an independent reference implementation or verified standard.
- ESTIMATED:  Derived from analytical roofline models or theoretical bounds (never promoted to MEASURED).
- SIMULATED:  Derived from simulation models (never cited as physical execution).
- CACHED:     Retrieved from an exact cache without computation.
- PREDICTIVE: Speculative draft or surrogate model output prior to verification.
- APPROXIMATE: Output generated under a bounded numerical or perceptual tolerance contract.
- UNKNOWN:    Uncharacterized or unverified data (defaults to fail-closed).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class EvidenceProvenance(str, Enum):
    MEASURED = "MEASURED"
    REFERENCE = "REFERENCE"
    ESTIMATED = "ESTIMATED"
    SIMULATED = "SIMULATED"
    CACHED = "CACHED"
    PREDICTIVE = "PREDICTIVE"
    APPROXIMATE = "APPROXIMATE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ProvenanceTag:
    provenance_class: EvidenceProvenance
    source_identifier: str
    timestamp: float
    measurement_tool: str = "time.perf_counter_ns"
    notes: Optional[str] = None
