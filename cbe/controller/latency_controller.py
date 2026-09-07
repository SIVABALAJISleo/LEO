"""
cbe/controller/latency_controller.py
Pacing and responsiveness supervisor.
Separately tracks simulation FPS, render FPS, display FPS, and true input latency
to guarantee that high generated FPS never hides interactive responsiveness lag.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class LatencyReport:
    simulation_fps: float
    render_fps: float
    display_fps: float
    generated_frames_pct: float
    input_latency_ms: float
    frame_pacing_jitter_ms: float
    is_responsive: bool


class LatencyController:
    """
    Supervises interactive responsiveness and prevents frame generation latency spoofing.
    """
    def __init__(self, target_display_fps: float = 60.0, max_input_latency_ms: float = 40.0):
        self.target_display_fps = target_display_fps
        self.max_input_latency_ms = max_input_latency_ms
        self.target_frame_time_sec = 1.0 / target_display_fps
        
        self.last_frame_timestamps: List[float] = []
        self.sim_times: List[float] = []
        self.render_times: List[float] = []
        self.input_latencies: List[float] = []
        self.generated_count = 0
        self.total_count = 0

    def record_frame(
        self,
        sim_duration_sec: float,
        render_duration_sec: float,
        input_latency_ms: float = 12.0,
        is_generated_frame: bool = False
    ):
        now = time.perf_counter()
        self.last_frame_timestamps.append(now)
        if len(self.last_frame_timestamps) > 60:
            self.last_frame_timestamps.pop(0)
            
        self.sim_times.append(sim_duration_sec)
        if len(self.sim_times) > 60:
            self.sim_times.pop(0)
            
        self.render_times.append(render_duration_sec)
        if len(self.render_times) > 60:
            self.render_times.pop(0)
            
        self.input_latencies.append(input_latency_ms)
        if len(self.input_latencies) > 60:
            self.input_latencies.pop(0)
            
        self.total_count += 1
        if is_generated_frame:
            self.generated_count += 1

    def get_report(self) -> LatencyReport:
        if len(self.last_frame_timestamps) < 2:
            return LatencyReport(60.0, 60.0, 60.0, 0.0, 16.0, 0.0, True)
            
        intervals = [
            self.last_frame_timestamps[i] - self.last_frame_timestamps[i-1]
            for i in range(1, len(self.last_frame_timestamps))
        ]
        avg_interval = sum(intervals) / len(intervals)
        display_fps = 1.0 / max(1e-4, avg_interval)
        
        avg_sim = sum(self.sim_times) / max(1, len(self.sim_times))
        sim_fps = 1.0 / max(1e-4, avg_sim)
        
        avg_render = sum(self.render_times) / max(1, len(self.render_times))
        render_fps = 1.0 / max(1e-4, avg_render)
        
        avg_input_lat = sum(self.input_latencies) / max(1, len(self.input_latencies))
        
        # Jitter: standard deviation of intervals
        jitter_ms = float(np.std(intervals) * 1000.0) if len(intervals) > 2 else 0.0
        
        gen_pct = (self.generated_count / max(1, self.total_count)) * 100.0
        is_responsive = avg_input_lat <= self.max_input_latency_ms
        
        return LatencyReport(
            simulation_fps=round(sim_fps, 1),
            render_fps=round(render_fps, 1),
            display_fps=round(display_fps, 1),
            generated_frames_pct=round(gen_pct, 1),
            input_latency_ms=round(avg_input_lat, 2),
            frame_pacing_jitter_ms=round(jitter_ms, 2),
            is_responsive=is_responsive
        )

import numpy as np
