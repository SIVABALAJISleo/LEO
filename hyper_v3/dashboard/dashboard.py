"""
hyper_v3/dashboard/dashboard.py
Live terminal status and metrics dashboard for HYPER 3.0.
"""

from typing import Dict, Any
from hyper_v3.runtime.device_manager import DeviceManager


class TerminalDashboard:
    """Renders real-time execution statistics to the console."""

    @staticmethod
    def render_status(workload_name: str, strategy: str, vwa: float, latency_us: float, verified: bool) -> str:
        dev_mgr = DeviceManager()
        prof = dev_mgr.get_hardware_profile()
        status_str = f"""
================================================================================
                    HYPER 3.0 AUTONOMOUS DASHBOARD
================================================================================
[HOST CPU]      {prof['cpu']['name']} ({prof['cpu']['physical_cores']}C/{prof['cpu']['logical_cores']}T, {prof['cpu']['ram_gb']}GB RAM)
[TARGET iGPU]   {prof['igpu']['name']} ({prof['igpu']['runtime']})
--------------------------------------------------------------------------------
WORKLOAD:       {workload_name}
STRATEGY:       {strategy}
LATENCY:        {latency_us:,.1f} µs
VWA AVOIDANCE:  {vwa*100:.1f}%
VERIFICATION:   {'PASS' if verified else 'FAIL'}
================================================================================
"""
        return status_str
