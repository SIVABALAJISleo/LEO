"""
core_ai/bitnet/intel_amx_accelerator.py
Compatibility wrapper redirecting to intel_vnni_accelerator.py.
Hardware clarification: i5-12450H utilizes Intel DL Boost VNNI (AVX2/FMA/VPDPBUSD), as AMX is Xeon-exclusive.
"""

from core_ai.bitnet.intel_vnni_accelerator import IntelVNNIAccelerator

class IntelAMXAccelerator(IntelVNNIAccelerator):
    """
    Alias maintained for backwards compatibility across legacy benchmark scripts.
    Directs execution through Intel DL Boost VNNI DP4A accelerator.
    """
    def __init__(self):
        super().__init__()
        self.amx_supported = self.vnni_supported
        self.tile_config = {
            "mode": "INTEL_DL_BOOST_VNNI",
            "instruction": "VPDPBUSD",
            "note": "Mapped to Alder Lake VNNI for i5-12450H CPU"
        }

    def ternary_matmul_amx(self, weights, activations):
        return self.ternary_matmul_vnni(weights, activations)

