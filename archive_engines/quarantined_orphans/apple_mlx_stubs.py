"""
archive_engines/quarantined_orphans/apple_mlx_stubs.py
======================================================
Quarantined Apple Silicon MLX / Metal execution stubs.
Platform Target: Intel Core i5-12450H + Intel UHD Graphics 48-EU (Windows / Linux).
Non-target Apple hardware runtimes quarantined out of active execution graph.
"""

from typing import AsyncIterator

def _has_mlx() -> bool:
    """Quarantined probe for Apple Silicon MLX."""
    return False

async def _generate_mlx(prompt: str, model_path: str, device_plan: dict) -> AsyncIterator[str]:
    """Quarantined execution loop for Apple Silicon MLX."""
    raise NotImplementedError(
        "Apple MLX is quarantined. Target hardware is Intel Core i5-12450H + Intel UHD Graphics."
    )
    yield ""
