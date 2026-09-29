"""
hyper_x/rtx5090/live_probe.py
=============================================================================
HYPER-Ω: Physical RTX 5090 Live Probe & Anti-Simulation Guard (Sections 30 & 31)
=============================================================================
CRITICAL SCIENTIFIC INTEGRITY RULE:
1. NEVER simulate an RTX 5090.
2. NEVER use theoretical NVIDIA specifications as runtime timings.
3. NEVER invent GPU measurements.
4. NEVER claim live parity without verified physical hardware execution.

If an actual RTX 5090 GPU is NOT physically attached and detected:
    RTX5090_STATUS = "UNAVAILABLE"
and the system halts comparison rather than fabricating numbers.
"""

from __future__ import annotations
import os
import sys
import subprocess
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class RTX5090ProbeResult:
    status: str  # "AVAILABLE" or "UNAVAILABLE"
    gpu_name: Optional[str]
    driver_version: Optional[str]
    cuda_available: bool
    device_count: int
    is_live_rtx5090: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "gpu_name": self.gpu_name,
            "driver_version": self.driver_version,
            "cuda_available": self.cuda_available,
            "device_count": self.device_count,
            "is_live_rtx5090": self.is_live_rtx5090,
            "notes": self.notes,
        }


class RTX5090LiveProbe:
    """
    Physically probes the host system for an actual live NVIDIA RTX 5090.
    """

    @staticmethod
    def probe_hardware() -> RTX5090ProbeResult:
        # Check 1: nvidia-smi
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                lines = res.stdout.strip().split("\n")
                first_line = lines[0].split(",")
                gpu_name = first_line[0].strip()
                driver_ver = first_line[1].strip() if len(first_line) > 1 else "Unknown"
                is_5090 = "5090" in gpu_name

                if is_5090:
                    return RTX5090ProbeResult(
                        status="AVAILABLE",
                        gpu_name=gpu_name,
                        driver_version=driver_ver,
                        cuda_available=True,
                        device_count=len(lines),
                        is_live_rtx5090=True,
                        notes="Live NVIDIA RTX 5090 physically detected via nvidia-smi.",
                    )
                else:
                    return RTX5090ProbeResult(
                        status="UNAVAILABLE",
                        gpu_name=gpu_name,
                        driver_version=driver_ver,
                        cuda_available=True,
                        device_count=len(lines),
                        is_live_rtx5090=False,
                        notes=f"Detected NVIDIA GPU ({gpu_name}), but not an RTX 5090. Live 5090 parity comparison is UNAVAILABLE.",
                    )
        except Exception:
            pass

        # Check 2: PyTorch CUDA if installed
        try:
            import torch
            if torch.cuda.is_available():
                count = torch.cuda.device_count()
                name = torch.cuda.get_device_name(0) if count > 0 else "Unknown"
                is_5090 = "5090" in name
                return RTX5090ProbeResult(
                    status="AVAILABLE" if is_5090 else "UNAVAILABLE",
                    gpu_name=name,
                    driver_version=None,
                    cuda_available=True,
                    device_count=count,
                    is_live_rtx5090=is_5090,
                    notes="Live RTX 5090 detected via PyTorch" if is_5090 else f"CUDA device {name} is not RTX 5090. Live comparison UNAVAILABLE.",
                )
        except ImportError:
            pass

        # Host has no NVIDIA GPU attached (Target Device: Intel Core i5-12450H + Intel UHD Graphics)
        return RTX5090ProbeResult(
            status="UNAVAILABLE",
            gpu_name=None,
            driver_version=None,
            cuda_available=False,
            device_count=0,
            is_live_rtx5090=False,
            notes="No physical NVIDIA GPU detected on host. Target device is Intel Core i5-12450H + Intel UHD Graphics. Live RTX 5090 execution is strictly UNAVAILABLE. Zero simulation permitted.",
        )
