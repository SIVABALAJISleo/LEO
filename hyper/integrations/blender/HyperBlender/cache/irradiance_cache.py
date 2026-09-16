"""
hyper/integrations/blender/HyperBlender/cache/irradiance_cache.py
"""
import numpy as np
from typing import Dict, Optional

class BlenderIrradianceCache:
    """Caches baking and irradiance probe grids across keyframes."""
    def __init__(self):
        self.probe_cache: Dict[str, np.ndarray] = {}

    def store_probe(self, probe_id: str, irradiance_data: np.ndarray):
        self.probe_cache[probe_id] = irradiance_data.copy()

    def get_probe(self, probe_id: str) -> Optional[np.ndarray]:
        return self.probe_cache.get(probe_id)
