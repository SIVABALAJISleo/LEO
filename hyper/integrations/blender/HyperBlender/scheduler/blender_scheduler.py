"""
hyper/integrations/blender/HyperBlender/scheduler/blender_scheduler.py
"""
class BlenderScheduler:
    """Routes rendering tasks between CPU AVX2 (Cycles CPU threads) and Intel UHD iGPU (Eevee / OpenVINO)."""
    def route_task(self, mode: str, is_viewport: bool) -> str:
        if is_viewport:
            # Interactive viewport: Use Eevee / OpenCL / iGPU accelerated path
            return "IGPU_VIEWPORT_PATH"
        else:
            # Final production render: Use full CPU AVX2 multi-threaded path
            return "CPU_CYCLES_PATH"
