#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/telemetry/monitor.py
============================
Phase 11: Host Silicon Live Telemetry Monitor.
Captures CPU utilization, memory RSS, and package temperature.
"""

import psutil
import time
from typing import Dict, Any


class TelemetryMonitor:
    """Captures live system telemetry during execution."""

    @staticmethod
    def sample() -> Dict[str, Any]:
        proc = psutil.Process()
        ram_mb = proc.memory_info().rss / (1024 * 1024)
        cpu_pct = psutil.cpu_percent(interval=None)

        return {
            "timestamp": time.time(),
            "cpu_utilization_pct": cpu_pct,
            "process_rss_mb": round(ram_mb, 2),
            "system_ram_available_mb": round(psutil.virtual_memory().available / (1024 * 1024), 2),
            "thread_count": proc.num_threads()
        }
