"""
hyper_universal/analysis/bottleneck.py
Bottleneck Analyzer & Roofline Model:
Analyzes computational IR graphs against host hardware limits (Intel Core i5 AVX2 + DDR RAM bus)
to classify bottlenecks (memory-bound vs compute-bound) and recommend optimization strategies.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List
import numpy as np

from hyper_universal.workload_ir.graph import ComputationalIR


class BottleneckClassification(str, Enum):
    MEMORY_BANDWIDTH_BOUND = "MEMORY_BANDWIDTH_BOUND"
    CACHE_CAPACITY_BOUND = "CACHE_CAPACITY_BOUND"
    COMPUTE_BOUND = "COMPUTE_BOUND"
    DISPATCH_OVERHEAD_BOUND = "DISPATCH_OVERHEAD_BOUND"


@dataclass
class BottleneckAnalysisReport:
    classification: BottleneckClassification
    arithmetic_intensity_flops_per_byte: float
    roofline_knee_flops_per_byte: float
    estimated_flops: int
    estimated_memory_bytes: int
    recommended_engines: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification.value,
            "arithmetic_intensity_flops_per_byte": round(self.arithmetic_intensity_flops_per_byte, 2),
            "roofline_knee_flops_per_byte": round(self.roofline_knee_flops_per_byte, 2),
            "estimated_flops": self.estimated_flops,
            "estimated_memory_bytes": self.estimated_memory_bytes,
            "recommended_engines": self.recommended_engines,
            "explanation": self.explanation,
        }


class BottleneckAnalyzer:
    """Classifies computational bottlenecks using host roofline models."""

    def __init__(self, host_peak_gflops: float = 250.0, host_memory_bw_gbps: float = 18.57):
        self.host_peak_gflops = host_peak_gflops
        self.host_memory_bw_gbps = host_memory_bw_gbps
        # Roofline transition knee point: Peak FLOPs / Peak Bandwidth
        self.roofline_knee = host_peak_gflops / max(host_memory_bw_gbps, 1.0)  # ~13.5 FLOPs/byte

    def analyze(self, ir: ComputationalIR) -> BottleneckAnalysisReport:
        flops = ir.get_total_flops()
        mem_bytes = ir.get_peak_intermediate_memory()
        for inp in ir.inputs:
            if inp in ir.nodes:
                mem_bytes += ir.nodes[inp].memory_bytes

        intensity = flops / max(mem_bytes, 1)

        # Dispatch latency check: tiny workloads (< 100k FLOPs)
        if flops < 100_000:
            classification = BottleneckClassification.DISPATCH_OVERHEAD_BOUND
            recs = ["CPU_INLINE_EXECUTION", "KERNEL_FUSION"]
            expl = "Workload is too small to overcome thread dispatch or GPU launch overhead; inline CPU AVX2 recommended."
        elif intensity < self.roofline_knee:
            # Memory bandwidth bound
            if mem_bytes > 32 * 1024 * 1024:  # Exceeds L3 cache (12 MB on i5-12450H)
                classification = BottleneckClassification.MEMORY_BANDWIDTH_BOUND
                recs = ["MEMORY_ESCAPE_STREAMING", "CACHE_BLOCKING_TILING", "QUANTIZATION_INT8"]
                expl = f"Arithmetic intensity ({intensity:.2f} FLOPs/B) is below roofline knee ({self.roofline_knee:.2f}). Working set exceeds L3 cache, causing DDR RAM streaming stall."
            else:
                classification = BottleneckClassification.CACHE_CAPACITY_BOUND
                recs = ["CACHE_BLOCKING_TILING", "IN_PLACE_EXECUTION"]
                expl = "Working set fits within L2/L3 cache hierarchy; cache tiling and loop blocking recommended."
        else:
            # Compute bound
            classification = BottleneckClassification.COMPUTE_BOUND
            recs = ["COMPUTATION_ELIMINATION_SPARSITY", "FFT_CONVOLUTION", "LOW_RANK_FACTORIZATION"]
            expl = f"High arithmetic intensity ({intensity:.2f} FLOPs/B) saturates ALU throughput. Algorithmic work elimination recommended."

        return BottleneckAnalysisReport(
            classification=classification,
            arithmetic_intensity_flops_per_byte=intensity,
            roofline_knee_flops_per_byte=self.roofline_knee,
            estimated_flops=flops,
            estimated_memory_bytes=mem_bytes,
            recommended_engines=recs,
            explanation=expl,
        )
