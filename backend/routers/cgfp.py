"""
backend/routers/cgfp.py
FastAPI Router for Project LEO-Frame: Contract-Gated Frame Pipeline (CGFP)
Provides real-time frame pacing, thermal hysteresis control, and lever actuation for Cyberpunk 2077 on Intel UHD iGPU.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from leo.cgfp_frame_governor import get_cgfp_governor

router = APIRouter(prefix="/api/v1/cgfp", tags=["CGFP Cyberpunk Governor"])

class ActuateRequest(BaseModel):
    render_scale_pct: Optional[float] = None
    xess_mode: Optional[str] = None
    fps_cap: Optional[int] = None
    texture_tier: Optional[str] = None

class TickRequest(BaseModel):
    simulated_load_pct: Optional[float] = 85.0

@router.get("/status")
async def get_cgfp_status():
    """Returns current real-time telemetry, thermal status, active levers, and contract adherence"""
    governor = get_cgfp_governor()
    return governor.get_summary()

@router.post("/tick")
async def process_frame_tick(req: TickRequest):
    """Processes a governor control tick and returns updated frame telemetry"""
    governor = get_cgfp_governor()
    telemetry = governor.tick(simulated_load_pct=req.simulated_load_pct or 85.0)
    return {
        "status": "success",
        "telemetry": {
            "base_fps": telemetry.base_fps,
            "perceived_fps": telemetry.perceived_fps,
            "frame_time_ms": telemetry.frame_time_ms,
            "frame_time_p99_ms": telemetry.frame_time_p99_ms,
            "package_temp_celsius": telemetry.package_temp_celsius,
            "clock_frequency_ghz": telemetry.clock_frequency_ghz,
            "clock_oscillation_pct": telemetry.clock_oscillation_pct,
            "render_scale_pct": telemetry.render_scale_pct,
            "xess_mode": telemetry.xess_mode,
            "contract_status": telemetry.contract_status
        }
    }

@router.post("/actuate")
async def actuate_levers(req: ActuateRequest):
    """Manually or adaptively overrides actuation levers"""
    governor = get_cgfp_governor()
    if req.render_scale_pct is not None:
        governor.render_scale_pct = req.render_scale_pct
    if req.xess_mode is not None:
        if req.xess_mode in governor.xess_modes:
            governor.current_xess_idx = governor.xess_modes.index(req.xess_mode)
    if req.fps_cap is not None:
        governor.fps_cap = req.fps_cap
    if req.texture_tier is not None:
        governor.texture_tier = req.texture_tier

    return {
        "status": "success",
        "message": "Levers actuated successfully",
        "current_levers": {
            "render_scale_pct": governor.render_scale_pct,
            "xess_mode": governor.xess_modes[governor.current_xess_idx],
            "fps_cap": governor.fps_cap,
            "texture_tier": governor.texture_tier
        }
    }

@router.get("/contract")
async def get_contract_definition():
    """Returns the formal YAML contract specification"""
    return {
        "contract_name": "contracts/cyberpunk_2077_igpu.yaml",
        "perceptual": "XeSS Balanced + FSR 3.0 Frame Generation + Tier-1 VRS",
        "interactive": "Perceived FPS >= 45 (Target: 60), p95 Input Latency <= 100ms, Zero Freeze",
        "thermal": "Package Temp <= 88°C (Hysteresis 3°C), Clock Oscillation < 5%",
        "hardware": "Intel Core i5-12450H (8c/12t) + Intel UHD Graphics (48 EUs, 50 GB/s RAM)"
    }
