"""
cbe/importance/importance_map.py
Unified importance field synthesizing perceptual, semantic, motion,
and foveated center-weighting into an actionable [0, 1] compute allocation map.
"""

from __future__ import annotations

import numpy as np
from typing import Optional

from .perceptual_importance import PerceptualImportance
from .semantic_importance import SemanticImportance
from .motion_importance import MotionImportance


class ImportanceMapEngine:
    """
    Fuses multiple psychological and visual metrics into a normalized importance field.
    Directly drives adaptive resolution scaling, Variable Rate Shading (VRS),
    and sparse ray-tracing budgets.
    """
    def __init__(
        self,
        weight_perceptual: float = 0.35,
        weight_semantic: float = 0.35,
        weight_motion: float = 0.15,
        weight_foveation: float = 0.15
    ):
        self.wp = weight_perceptual
        self.ws = weight_semantic
        self.wm = weight_motion
        self.wf = weight_foveation
        
        self.perceptual_eng = PerceptualImportance()
        self.semantic_eng = SemanticImportance()
        self.motion_eng = MotionImportance()

    def generate_foveation_mask(self, height: int, width: int, center_x: float = 0.5, center_y: float = 0.5) -> np.ndarray:
        """Generates radial foveation gradient centered at (center_x, center_y)."""
        y, x = np.mgrid[0:height, 0:width].astype(np.float32)
        nx = (x / max(1, width - 1)) - center_x
        ny = (y / max(1, height - 1)) - center_y
        dist_sq = nx**2 + ny**2
        # Center = 1.0, corners fall off to ~0.5
        mask = np.exp(-dist_sq / 0.5)
        return np.clip(mask, 0.4, 1.0).astype(np.float32)

    def generate_importance_map(
        self,
        color_buffer: np.ndarray,
        motion_vectors: Optional[np.ndarray] = None,
        semantic_map: Optional[np.ndarray] = None,
        focus_center: Optional[Tuple[float, float]] = None
    ) -> np.ndarray:
        """
        Synthesizes composite importance map.
        color_buffer: (H, W, 3) float32 in [0, 1].
        """
        H, W, C = color_buffer.shape
        
        # 1. Perceptual contrast
        p_map = self.perceptual_eng.compute(color_buffer)
        
        # 2. Semantic priority
        s_map = self.semantic_eng.compute(semantic_map, H, W)
        
        # 3. Motion masking
        if motion_vectors is not None:
            m_map = self.motion_eng.compute(motion_vectors)
        else:
            m_map = np.ones((H, W), dtype=np.float32)
            
        # 4. Foveated center bias
        cx, cy = focus_center if focus_center is not None else (0.5, 0.5)
        f_map = self.generate_foveation_mask(H, W, cx, cy)
        
        # Composite normalized sum
        composite = (self.wp * p_map + self.ws * s_map + self.wm * m_map + self.wf * f_map)
        return np.clip(composite, 0.0, 1.0).astype(np.float32)
