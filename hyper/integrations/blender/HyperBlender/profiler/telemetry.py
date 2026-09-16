"""
hyper/integrations/blender/HyperBlender/profiler/telemetry.py
"""
import time
from typing import Dict, Any

class BlenderProfiler:
    """Measures Blender viewport frame times, polygon throughput, and avoided shading work."""
    def __init__(self):
        self.frame_records: list = []

    def log_frame(self, frame_ms: float, poly_count: int, work_avoided_pct: float):
        self.frame_records.append({
            "timestamp": time.time(),
            "frame_ms": round(frame_ms, 2),
            "poly_count": poly_count,
            "work_avoided_pct": round(work_avoided_pct, 2),
        })
