"""
hyper_universal/capability_mirror/matrix.py
Universal Capability Matrix Report Generator:
Evaluates all 21 reference GPU capabilities across CPU AVX2, Intel UHD iGPU, Emulation,
and Algorithmic pathways, emitting comprehensive audit JSON and markdown matrices.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from hyper_universal.capability_mirror.registry import UniversalCapabilityRegistry
from hyper_universal.capability_mirror.search import CapabilitySubstitutionSearch, SubstitutionCandidate


class CapabilityMatrixGenerator:
    """
    Generates a full capability audit matrix across all 21 hardware functions.
    """

    def __init__(self):
        self.registry = UniversalCapabilityRegistry()
        self.search_engine = CapabilitySubstitutionSearch(registry=self.registry)

    def evaluate_all(self) -> Dict[str, Any]:
        """
        Runs substitution search across every registered GPU capability.
        """
        results: Dict[str, List[Dict[str, Any]]] = {}
        total_caps = 0
        total_substitutions_found = 0
        verified_substitutions = 0

        for cap in self.registry.list_capabilities():
            total_caps += 1
            candidates = self.search_engine.search_substitution(cap.capability_id)
            total_substitutions_found += len(candidates)
            c_dicts = []
            for c in candidates:
                if c.is_correctness_verified:
                    verified_substitutions += 1
                c_dicts.append(c.to_dict())
            results[cap.capability_id] = c_dicts

        report = {
            "total_capabilities_evaluated": total_caps,
            "total_candidate_pathways": total_substitutions_found,
            "verified_substitutions_count": verified_substitutions,
            "hardware_platform": "Intel Core i5-12450H + Intel UHD Graphics iGPU (Windows 11)",
            "matrix": results,
        }
        return report

    def generate_markdown_report(self) -> str:
        """Emits a GitHub-flavored Markdown capability matrix."""
        audit = self.evaluate_all()
        lines = [
            "# UNIVERSAL GPU CAPABILITY MIRROR MATRIX",
            "",
            f"**Platform**: {audit['hardware_platform']}  ",
            f"**Total Evaluated Hardware Functions**: {audit['total_capabilities_evaluated']}  ",
            f"**Candidate Software Pathways Evaluated**: {audit['total_candidate_pathways']}  ",
            f"**Verified Correct Substitutions**: {audit['verified_substitutions_count']}  ",
            "",
            "| Capability ID | Reference GPU Function | Pathway Evaluated | Latency (ms) | Speedup vs Ref | Correctness | Equivalence Dimensions | Status |",
            "|:---|:---|:---|:---|:---|:---|:---|:---|",
        ]

        for cap_id, candidates in audit["matrix"].items():
            cap_record = self.registry.get(cap_id)
            ref_name = cap_record.hardware_function[:40] + "..." if cap_record else cap_id
            for c in candidates:
                eq_dims = []
                for dim, active in c["equivalence_ratings"].items():
                    if active and dim != "PHYSICAL_HARDWARE":
                        eq_dims.append(dim[:4])
                eq_str = ",".join(eq_dims) if eq_dims else "None"
                is_ok = "PASS" if c["is_correctness_verified"] else "FAIL"
                lines.append(
                    f"| `{cap_id}` | {ref_name} | {c['substitution_type']} | {c['measured_latency_ms']} | {c['measured_speedup']}x | {is_ok} | {eq_str} | `{c['certification_status']}` |"
                )

        lines.extend([
            "",
            "## Equivalence Dimension Legend",
            "- `PHYSICAL_HARDWARE`: Physical discrete GPU silicon present (**False** across all tests on this laptop).",
            "- `API_EMU`: Instruction or API emulation layer (Vulkan / OpenCL / CPU emulated).",
            "- `FUNC`: Functional equivalence (produces exact identical outcomes).",
            "- `MATH`: Mathematical equivalence under floating-point precision bounds.",
            "- `APPL`: Application-contract equivalence (meets application declared tolerances).",
            "- `PERF`: Performance equivalence (matches or exceeds reference latency).",
            "",
            "## Unresolved Gaps & Next Proposed Experiments",
            "1. **Ray Tracing Fixed Functions**: BVH traversal and ray intersection rely on CPU BVH traversal; next experiment is integrating Intel Embree CPU SIMD traversal.",
            "2. **Very Large GEMMs (>4096)**: Limited by 18.57 GB/s host memory bandwidth; next experiment is multi-block out-of-core streaming with OpenVINO INT8 weights.",
            "3. **Fixed Hardware Texture Samplers**: Software bilinear filtering is ALU-bound; next experiment is tiled texture caching with AVX2 gather instructions.",
        ])
        return "\n".join(lines)
