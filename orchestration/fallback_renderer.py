import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FallbackRenderer:
    """
    Nuclear Fallback Module: Forces software-based rendering.
    Uses Mesa LLVMpipe or SwiftShader for compatibility without GPU.
    """
    def __init__(self):
        logger.info("FallbackRenderer initialized (Nuclear Fallback)")

    def force_software_env(self) -> Dict[str, str]:
        """
        Provides environment variables to force software rendering.
        """
        logger.warning("FORCING SOFTWARE RENDERER (LLVMPipe/SwiftShader)")
        
        env_updates = {
            "LIBGL_ALWAYS_SOFTWARE": "1",
            "GALLIUM_DRIVER": "llvmpipe",
        }
        
        # If on Windows, we might point to specific DLLs if bundled
        if os.name == 'nt':
            env_updates["VK_ICD_FILENAMES"] = "./swiftshader/vk_swiftshader_icd.json"
        else:
             env_updates["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/lvp_icd.x86_64.json"
             
        return env_updates

    def render_offline_frame(self, scene_data: Dict[str, Any]) -> str:
        """
        Slow, offline software rasterization for one frame.
        """
        logger.info("Executing slow software render for compatibility")
        # In a real system, this might call a CLI tool like Blender or a custom rasterizer
        # For now, we return a placeholder path
        return "data/exports/software_render_frame_01.png"

    def is_gpu_needed(self, task_complexity: str) -> bool:
        """
        Decision logic: If task is 'GPU_HEAVY', this engine should NOT run it live.
        It should instead use this software fallback or proxies.
        """
        # In our CPU-first philosophy, we NEVER need a GPU for logic. 
        # But if the USER requests a high-fidelity render that we can't bake, this returns True
        # to trigger the fallback path.
        return task_complexity == "GPU_HEAVY"
