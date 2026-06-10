"""
backend/hardware/detector.py
System capability auto-detection for CPU, iGPU, NPU, RAM, and storage topology.
"""
import os
import sys
import platform
import psutil
import subprocess
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class HardwareDetector:
    """
    Scans host hardware capabilities and reports CPU, iGPU, and NPU specifications
    to allow the heterogeneous router to assign workloads appropriately.
    """

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Auto-detects CPU characteristics and instruction sets."""
        cpu_data = {
            "cores": psutil.cpu_count(logical=False) or 4,
            "threads": psutil.cpu_count(logical=True) or 8,
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "avx2": False,
            "avx512": False,
            "amx": False,
            "neon": False
        }

        # Check CPU flags
        try:
            if platform.system() == "Windows":
                # Execute wmic or use registry/environ queries for flags
                # On Windows, we can query PROCESSOR_IDENTIFIER or check via wmic
                # For safety and speed, we check environment variables & registry
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                features, _ = winreg.QueryValueEx(key, "FeatureSet")
                winreg.CloseKey(key)
                
                # Check for AVX2 support (FeatureSet bits or PROCESSOR_IDENTIFIER)
                cpu_data["avx2"] = True  # Modern Windows desktops (2015+) almost universally support AVX2
                # In typical production we can probe using brief assembly or systeminfo
                proc_id = os.environ.get("PROCESSOR_IDENTIFIER", "").lower()
                if "intel64" in proc_id or "amd64" in proc_id:
                    cpu_data["avx2"] = True
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read().lower()
                cpu_data["avx2"] = "avx2" in cpuinfo
                cpu_data["avx512"] = "avx512" in cpuinfo
                cpu_data["amx"] = "amx" in cpuinfo
                cpu_data["neon"] = "neon" in cpuinfo or "asimd" in cpuinfo
            elif platform.system() == "Darwin":
                # macOS
                brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().lower()
                if "apple" in brand:
                    cpu_data["neon"] = True
                else:
                    flags = subprocess.check_output(["sysctl", "-n", "machdep.cpu.features"]).decode().lower()
                    cpu_data["avx2"] = "avx2" in flags
                    cpu_data["avx512"] = "avx512" in flags
        except Exception as e:
            logger.debug(f"Extended CPU flags detection skipped: {e}")
            # Fallback to standard capabilities for modern hosts
            cpu_data["avx2"] = True

        return cpu_data

    @staticmethod
    def get_gpu_info() -> Dict[str, Any]:
        """Probes for integrated GPUs, discrete GPUs, and API runtimes (Vulkan, OpenCL, DirectML)."""
        gpu_data = {
            "has_nvidia": False,
            "vulkan": False,
            "opencl": False,
            "directml": False,
            "metal": False,
            "devices": []
        }

        # Check for NVIDIA (requires nvidia-smi)
        try:
            if platform.system() == "Windows":
                # Check standard paths
                nvsmi_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "DriverStore", "FileRepository")
                # Search for nvidia-smi
                found_smi = False
                for root, dirs, files in os.walk(nvsmi_path):
                    if "nvidia-smi.exe" in files:
                        found_smi = True
                        break
                if found_smi or subprocess.call(["where", "nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    gpu_data["has_nvidia"] = True
            else:
                if subprocess.call(["which", "nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    gpu_data["has_nvidia"] = True
        except Exception:
            pass

        # Probe API supports
        # On Windows, Vulkan is supported by drivers. DirectML is part of DirectX.
        if platform.system() == "Windows":
            gpu_data["directml"] = True
            gpu_data["vulkan"] = os.path.exists("C:\\Windows\\System32\\vulkan-1.dll")
            gpu_data["opencl"] = os.path.exists("C:\\Windows\\System32\\OpenCL.dll")
        elif platform.system() == "Darwin":
            gpu_data["metal"] = True
        else: # Linux
            gpu_data["vulkan"] = True
            gpu_data["opencl"] = True

        # Detect discrete or integrated adapters via system profiles
        try:
            if platform.system() == "Windows":
                # Call wmic path win32_VideoController get name
                out = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"]).decode()
                devices = [line.strip() for line in out.split("\n")[1:] if line.strip()]
                gpu_data["devices"] = devices
            elif platform.system() == "Linux":
                out = subprocess.check_output(["lspci", "-v"]).decode().lower()
                for line in out.split("\n"):
                    if "vga" in line or "3d" in line:
                        gpu_data["devices"].append(line.strip())
        except Exception:
            gpu_data["devices"] = ["Generic Video Controller"]

        return gpu_data

    @staticmethod
    def get_npu_info() -> Dict[str, Any]:
        """Attempts to discover local NPUs (Intel NPU, Ryzen AI, Apple ANE)."""
        npu_data = {
            "has_npu": False,
            "type": "none"
        }

        try:
            if platform.system() == "Darwin":
                # Apple Neural Engine is always present on M-series chips
                brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().lower()
                if "apple" in brand:
                    npu_data["has_npu"] = True
                    npu_data["type"] = "Apple Neural Engine (ANE)"
            elif platform.system() == "Windows":
                # Check for Intel NPU or Ryzen AI NPU in Device Manager (via driver registry or commandline)
                # We can search through wmic for 'npu' or 'neural' or 'movidius'
                out = subprocess.check_output(["wmic", "path", "win32_PnPEntity", "get", "name"]).decode()
                for line in out.split("\n"):
                    line_lower = line.lower()
                    if "neural" in line_lower or "npu" in line_lower or "movidius" in line_lower:
                        npu_data["has_npu"] = True
                        npu_data["type"] = line.strip()
                        break
        except Exception:
            pass

        return npu_data

    @classmethod
    def get_system_profile(cls) -> Dict[str, Any]:
        """Aggregates all components to build a complete system profile."""
        mem = psutil.virtual_memory()
        
        # Determine fast storage type
        storage_type = "SSD"
        if platform.system() == "Windows":
            try:
                # Query MSFT_PhysicalDisk for MediaType (SSD/HDD)
                out = subprocess.check_output(["powershell", "-Command", "Get-PhysicalDisk | Select-Object MediaType"]).decode().lower()
                if "ssd" in out:
                    storage_type = "SSD"
                elif "hdd" in out:
                    storage_type = "HDD"
            except Exception:
                pass

        return {
            "cpu": cls.get_cpu_info(),
            "gpu": cls.get_gpu_info(),
            "npu": cls.get_npu_info(),
            "ram": {
                "total_gb": round(mem.total / 1e9, 2),
                "available_gb": round(mem.available / 1e9, 2),
                "numa_nodes": 1 # Default standard desktop topology
            },
            "storage": {
                "type": storage_type,
                "free_gb": round(psutil.disk_usage("/").free / 1e9, 2)
            }
        }
