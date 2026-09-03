"""
hyper_v3/transforms/tiling.py
Hardware-aware multi-level tiling and subgroup parameters for CPU and Intel UHD iGPU.
"""

from dataclasses import dataclass


@dataclass
class HardwareTilingParameters:
    workgroup_size_x: int = 16
    workgroup_size_y: int = 16
    subgroup_size: int = 16  # Intel GPU EU SIMD16
    local_memory_bytes: int = 4096
    tile_m: int = 32
    tile_n: int = 32
    tile_k: int = 16


class TilingTransformer:
    """Computes workgroup, subgroup, and local memory tiling parameters."""

    @staticmethod
    def compute_igpu_tiles(m: int, n: int, k: int) -> HardwareTilingParameters:
        # Intel UHD Graphics standard workgroup & subgroup configuration
        return HardwareTilingParameters(
            workgroup_size_x=16,
            workgroup_size_y=16,
            subgroup_size=16,
            local_memory_bytes=4096,
            tile_m=32,
            tile_n=32,
            tile_k=16
        )
