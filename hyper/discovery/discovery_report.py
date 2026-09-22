"""
hyper/discovery/discovery_report.py
===================================
Formal Schema for PathwayDiscoveryReport (Section 42).

Strict structured report conforming to all required scientific, performance,
and verification metrics.
"""

from __future__ import annotations
import uuid
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.capability_decomposer import CapabilityFamily


class PathwayDiscoveryReport(BaseModel):
    """
    Complete scientific report for every investigated or discovered computational pathway.
    """
    pathway_id: str
    workload: str
    capability: str
    original_method: str
    discovered_method: str
    transformations: List[str] = Field(default_factory=list)
    mathematical_basis: str = ""
    dependencies: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    certificate: Dict[str, Any] = Field(default_factory=dict)
    verification: Dict[str, Any] = Field(default_factory=dict)
    adversarial_testing: Dict[str, Any] = Field(default_factory=dict)
    reference_result: Dict[str, Any] = Field(default_factory=dict)
    candidate_result: Dict[str, Any] = Field(default_factory=dict)
    exactness: str = "EXACT"
    numerical_error: float = 0.0
    execution_time: Dict[str, float] = Field(default_factory=dict)  # {"reference_ms": ..., "candidate_ms": ...}
    memory: Dict[str, float] = Field(default_factory=dict)          # {"peak_ram_mb": ..., "bandwidth_gb_s": ...}
    cpu_usage: float = 0.0
    igpu_usage: float = 0.0
    thermal: float = 55.0  # Celsius
    power: float = 15.0    # Watts
    fallback_probability: float = 0.001
    speedup: float = 1.0
    work_reduction: float = 0.0  # percentage
    status: str = "DISCOVERED"   # DISCOVERED, IMPLEMENTED, VERIFIED, MEASURED, OPTIMIZED, COMPOSED, PRODUCTION_CANDIDATE, FAILED, UNKNOWN
    evidence_level: str = "MEASURED"  # PROVEN, MEASURED, DERIVED, ESTIMATED, HYPOTHESIS, UNVERIFIED, FAILED
    reproducibility: Dict[str, Any] = Field(default_factory=dict)

    def to_formatted_markdown(self) -> str:
        return f"""### Pathway Discovery Report: `{self.pathway_id}`
- **Workload**: `{self.workload}` | **Capability**: `{self.capability}`
- **Original Method**: {self.original_method}
- **Discovered Method**: {self.discovered_method}
- **Status**: `{self.status}` | **Evidence Level**: `{self.evidence_level}`
- **Speedup**: **{self.speedup:.2f}x** | **Work Reduction**: **{self.work_reduction:.1f}%**
- **Exactness**: `{self.exactness}` | **Numerical Error**: `{self.numerical_error:.2e}`
- **Execution Time**: Candidate {self.execution_time.get('candidate_ms', 0.0):.2f} ms vs Ref {self.execution_time.get('reference_ms', 0.0):.2f} ms
- **Hardware Telemetry**: CPU {self.cpu_usage:.1f}%, iGPU {self.igpu_usage:.1f}%, Power {self.power:.1f}W, Temp {self.thermal:.1f}°C
- **Mathematical Basis**: {self.mathematical_basis or 'N/A'}
"""
