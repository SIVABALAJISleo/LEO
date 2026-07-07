"""
backend/hardware/detector.py
Layer 1 — Silicon Awakening: System capability auto-detection for CPU, iGPU, NPU,
RAM, and storage topology. Detects every compute unit on the user's machine:
  - iGPU via Vulkan (vulkaninfo/pyvulkan) → OpenCL (clinfo) fallback
  - NPU via OS-specific enumeration (Windows DirectML, Linux /sys/class/accel/, macOS CoreML)
  - CPU ISA extensions: AMX, AVX-512 VNNI, AVX2, NEON (ARM SME)
Returns a unified HardwareProfile dataclass consumed by router.py and universal_execution.py.
"""

from __future__ import annotations

import os
import platform
import subprocess
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CPUProfile:
    cores: int
    threads: int
    architecture: str
    processor: str
    avx2: bool = False
    avx512: bool = False
    avx512_vnni: bool = False
    amx: bool = False
    neon: bool = False
    sme: bool = False          # ARM SME (Scalable Matrix Extension)


@dataclass
class GPUProfile:
    vendor: str = "Unknown"
    vram_shared_mb: int = 0
    vulkan: bool = False
    opencl: bool = False
    directml: bool = False
    metal: bool = False
    devices: List[str] = field(default_factory=list)
    has_nvidia: bool = False
    igpu_detected: bool = False


@dataclass
class NPUProfile:
    vendor: str = "Unknown"
    tops: int = 0
    api: str = "none"
    has_npu: bool = False
    type: str = "none"


@dataclass
class HardwareProfile:
    cpu: CPUProfile
    igpu: GPUProfile
    dgpu: Optional[GPUProfile] = None
    npu: NPUProfile = field(default_factory=NPUProfile)
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0

    def get(self, key: str, default=None):
        """Mock dict interface for backward compatibility with older components."""
        d = asdict(self)
        d["ram"] = {"total_gb": self.ram_total_gb, "available_gb": self.ram_available_gb}
        return d.get(key, default)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run(cmd: List[str], timeout: int = 5) -> str:
    """Run a subprocess command and return stdout; empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout
    except Exception:
        return ""


def _command_exists(cmd: str) -> bool:
    check = "where" if platform.system() == "Windows" else "which"
    return subprocess.call(
        [check, cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0


# ── CPU Detection ─────────────────────────────────────────────────────────────

class HardwareDetector:
    """
    Scans host hardware capabilities and reports CPU, iGPU, and NPU specifications
    to allow the heterogeneous router to assign workloads appropriately.
    """

    @staticmethod
    def get_cpu_info() -> CPUProfile:
        import psutil

        cpu_prof = CPUProfile(
            cores=psutil.cpu_count(logical=False) or 4,
            threads=psutil.cpu_count(logical=True) or 8,
            architecture=platform.machine(),
            processor=platform.processor(),
        )

        # Primary: py-cpuinfo (most reliable cross-platform)
        try:
            import cpuinfo  # type: ignore
            info = cpuinfo.get_cpu_info()
            flags: List[str] = info.get("flags", [])
            cpu_prof.avx2 = "avx2" in flags
            cpu_prof.avx512 = any(f.startswith("avx512") for f in flags)
            cpu_prof.avx512_vnni = "avx512_vnni" in flags
            cpu_prof.amx = any(f.startswith("amx") for f in flags)
            cpu_prof.neon = "neon" in flags or "asimd" in flags
            # ARM SME — exposed as "sme" flag on Linux ARMv9
            cpu_prof.sme = "sme" in flags
            return cpu_prof
        except ImportError:
            pass

        # Fallback: platform-specific raw reads
        system = platform.system()
        if system == "Linux":
            try:
                cpuinfo_text = open("/proc/cpuinfo").read().lower()
                cpu_prof.avx2 = "avx2" in cpuinfo_text
                cpu_prof.avx512 = "avx512" in cpuinfo_text
                cpu_prof.avx512_vnni = "avx512_vnni" in cpuinfo_text
                cpu_prof.amx = "amx" in cpuinfo_text
                cpu_prof.neon = "neon" in cpuinfo_text or "asimd" in cpuinfo_text
                cpu_prof.sme = "sme" in cpuinfo_text
            except Exception:
                pass

        elif system == "Darwin":
            try:
                brand = _run(["sysctl", "-n", "machdep.cpu.brand_string"]).lower()
                if "apple" in brand:
                    cpu_prof.neon = True
                    # Apple M2+ has SME; detect via hw.optional.arm.FEAT_SME
                    sme_out = _run(["sysctl", "-n", "hw.optional.arm.FEAT_SME"])
                    cpu_prof.sme = sme_out.strip() == "1"
                else:
                    feats = _run(["sysctl", "-n", "machdep.cpu.features"]).lower()
                    cpu_prof.avx2 = "avx2" in feats
                    cpu_prof.avx512 = "avx512" in feats
                    cpu_prof.avx512_vnni = "avx512_vnni" in feats
            except Exception:
                pass

        elif system == "Windows":
            # Conservatively assume modern laptop has AVX2
            cpu_prof.avx2 = True

        return cpu_prof

    # ── GPU / iGPU Detection ──────────────────────────────────────────────────

    @staticmethod
    def get_gpu_info() -> GPUProfile:
        import psutil

        gpu_prof = GPUProfile()
        system = platform.system()

        # ── NVIDIA check (discrete GPU) ──────────────────────────────
        if system == "Windows":
            drv_root = os.path.join(
                os.environ.get("SystemRoot", r"C:\Windows"),
                "System32", "DriverStore", "FileRepository",
            )
            try:
                for root, _, files in os.walk(drv_root):
                    if "nvidia-smi.exe" in files:
                        gpu_prof.has_nvidia = True
                        break
            except Exception:
                pass
            if not gpu_prof.has_nvidia:
                gpu_prof.has_nvidia = _command_exists("nvidia-smi")
        else:
            gpu_prof.has_nvidia = _command_exists("nvidia-smi")

        # ── OS-level API presence ─────────────────────────────────────
        if system == "Windows":
            gpu_prof.directml = True
            gpu_prof.vulkan = os.path.exists(r"C:\Windows\System32\vulkan-1.dll")
            gpu_prof.opencl = os.path.exists(r"C:\Windows\System32\OpenCL.dll")

        elif system == "Darwin":
            gpu_prof.metal = True

        else:  # Linux
            # Try vulkaninfo --summary
            vk_out = _run(["vulkaninfo", "--summary"])
            if "Vulkan" in vk_out or "vulkan" in vk_out.lower():
                gpu_prof.vulkan = True
            # Fall back to pyvulkan
            if not gpu_prof.vulkan:
                try:
                    import vulkan  # type: ignore  # pyvulkan
                    gpu_prof.vulkan = True
                except ImportError:
                    pass
            # OpenCL via clinfo
            cl_out = _run(["clinfo", "--list"])
            if cl_out.strip():
                gpu_prof.opencl = True

        # ── Device enumeration ────────────────────────────────────────
        if system == "Windows":
            # wmic may be deprecated on newer Windows; use PowerShell as fallback
            wmic_out = _run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                timeout=8,
            )
            devices = [l.strip() for l in wmic_out.split("\n")[1:] if l.strip()]
            if not devices:
                ps_out = _run(
                    [
                        "powershell", "-Command",
                        "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
                    ],
                    timeout=8,
                )
                devices = [l.strip() for l in ps_out.splitlines() if l.strip()]
            gpu_prof.devices = devices

        elif system == "Linux":
            lspci_out = _run(["lspci", "-v"]).lower()
            for line in lspci_out.splitlines():
                if "vga" in line or "3d" in line or "display" in line:
                    gpu_prof.devices.append(line.strip())

        elif system == "Darwin":
            sp_out = _run(
                ["system_profiler", "SPDisplaysDataType"],
                timeout=10,
            )
            for line in sp_out.splitlines():
                if "Chipset Model" in line or "Chip" in line:
                    gpu_prof.devices.append(line.split(":", 1)[-1].strip())

        if gpu_prof.devices:
            gpu_prof.vendor = gpu_prof.devices[0]

        # Mark as iGPU if any non-NVIDIA device detected or no dGPU
        if gpu_prof.devices and not gpu_prof.has_nvidia:
            gpu_prof.igpu_detected = True

        # Try OpenVINO device enumeration for Intel iGPU
        try:
            import openvino as ov  # type: ignore
            core = ov.Core()
            ov_devices = core.available_devices
            if "GPU" in ov_devices or any(d.startswith("GPU") for d in ov_devices):
                gpu_prof.igpu_detected = True
                if not gpu_prof.devices:
                    gpu_prof.vendor = "Intel iGPU (OpenVINO)"
                    gpu_prof.devices = ["Intel iGPU (OpenVINO)"]
        except Exception:
            pass

        # vram_shared_mb: for iGPU, shared system RAM (50% heuristic)
        try:
            import psutil
            gpu_prof.vram_shared_mb = int(psutil.virtual_memory().total * 0.5 / (1024 * 1024))
        except Exception:
            gpu_prof.vram_shared_mb = 4096

        return gpu_prof

    # ── NPU Detection ─────────────────────────────────────────────────────────

    @staticmethod
    def get_npu_info() -> NPUProfile:
        npu_prof = NPUProfile()
        system = platform.system()

        if system == "Darwin":
            try:
                brand = _run(["sysctl", "-n", "machdep.cpu.brand_string"]).lower()
                if "apple" in brand:
                    npu_prof.has_npu = True
                    npu_prof.vendor = "Apple"
                    npu_prof.type = "Apple Neural Engine (ANE)"
                    npu_prof.api = "CoreML"
                    # ANE TOPS: M1=11, M2=15.8, M3=18, M4=38 — heuristic 11+
                    npu_prof.tops = 11
                    # Try coremltools to verify availability
                    try:
                        import coremltools as ct  # type: ignore
                        _ = ct.ComputeUnit.ALL
                        npu_prof.tops = 15  # confirmed present; conservative floor
                    except ImportError:
                        pass
            except Exception:
                pass

        elif system == "Windows":
            # 1. DirectML device enumeration via PowerShell
            ps_out = _run(
                [
                    "powershell", "-Command",
                    "Get-PnpDevice -Status OK | Select-Object FriendlyName | Format-List",
                ],
                timeout=10,
            )
            for line in ps_out.splitlines():
                line_lower = line.lower()
                if any(kw in line_lower for kw in ("neural", "npu", "movidius", "ryzen ai", "hexagon", "mtk")):
                    npu_prof.has_npu = True
                    npu_prof.vendor = line.split(":", 1)[-1].strip()
                    npu_prof.type = npu_prof.vendor
                    npu_prof.api = "DirectML"
                    npu_prof.tops = 10  # conservative baseline
                    break

            # 2. ONNX Runtime DML as secondary confirmation
            if not npu_prof.has_npu:
                try:
                    import onnxruntime as ort  # type: ignore
                    providers = ort.get_available_providers()
                    if "DmlExecutionProvider" in providers:
                        npu_prof.has_npu = True
                        npu_prof.vendor = "DirectML NPU/iGPU"
                        npu_prof.type = "DirectML NPU"
                        npu_prof.api = "DirectML"
                        npu_prof.tops = 8
                except ImportError:
                    pass

        elif system == "Linux":
            # /sys/class/accel/ exists on Linux kernels with NPU drivers (Intel VPU, etc.)
            accel_path = "/sys/class/accel/"
            if os.path.exists(accel_path):
                entries = os.listdir(accel_path)
                if entries:
                    npu_prof.has_npu = True
                    npu_prof.type = f"Linux NPU ({entries[0]})"
                    npu_prof.vendor = "Intel/AMD NPU"
                    npu_prof.api = "OpenVINO"
                    npu_prof.tops = 10

            # OpenVINO NPU check
            if not npu_prof.has_npu:
                try:
                    import openvino as ov  # type: ignore
                    core = ov.Core()
                    if "NPU" in core.available_devices:
                        npu_prof.has_npu = True
                        npu_prof.vendor = "Intel NPU"
                        npu_prof.type = "Intel Neural Processing Unit"
                        npu_prof.api = "OpenVINO"
                        npu_prof.tops = 10
                except Exception:
                    pass

        return npu_prof

    # ── Unified Profile ────────────────────────────────────────────────────────

    @classmethod
    def get_system_profile(cls) -> HardwareProfile:
        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_total = round(mem.total / 1e9, 2)
            ram_avail = round(mem.available / 1e9, 2)
        except Exception:
            ram_total = 8.0
            ram_avail = 4.0

        return HardwareProfile(
            cpu=cls.get_cpu_info(),
            igpu=cls.get_gpu_info(),
            npu=cls.get_npu_info(),
            ram_total_gb=ram_total,
            ram_available_gb=ram_avail,
        )
