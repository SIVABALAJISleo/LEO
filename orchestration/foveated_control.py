import logging
from typing import Dict

logger = logging.getLogger(__name__)

class FoveatedController:
    """
    Foveated Perceptual Computation Control.
    Allocates compute budget based on visual acuity (distance from gaze).
    """
    def __init__(self):
        self.gaze_pos = (0.5, 0.5) # Normalized text coords
        logger.info("Foveated Controller initialized")

    def get_lod_bias(self, screen_pos) -> int:
        """
        Return LOD bias (0 = full detail, higher = lower detail).
        """
        dist = ((screen_pos[0]-self.gaze_pos[0])**2 + (screen_pos[1]-self.gaze_pos[1])**2)**0.5
        if dist < 0.1: return 0
        if dist < 0.3: return 1
        return 2
