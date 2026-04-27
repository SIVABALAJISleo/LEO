import psutil
import logging
import platform
import subprocess
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HardwareDetector:
    """
    STEP 2: HARDWARE DETECTION
    Builds a capability profile of the local machine.
    """
    def detect_profile(self) -> Dict[str, Any]:
        profile = {
            "cpu_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "os": platform.system(),
            "has_igpu": False,
            "has_dgpu": False
        }
        
        # Windows-specific GPU detection
        if platform.system() == "Windows":
            try:
                # Basic check via wmic
                res = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
                if "Intel" in res or "Iris" in res:
                    profile["has_igpu"] = True
                if "NVIDIA" in res or "AMD" in res:
                    profile["has_dgpu"] = True
            except:
                pass
                
        return profile
