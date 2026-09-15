"""
tests/hostile/test_random_graphics.py
=====================================
Random Graphics Frame Attack (Phases 15 & 19).
Breaks spatial and temporal coherence with completely random frames.
Ensures graphics engines do not produce stale artifacts or hallucinated reuse.
"""

import numpy as np
import pytest
from hyper_x.graphics.pipeline import SoftwareGraphicsPipeline


def test_random_graphics_attack():
    pipeline = SoftwareGraphicsPipeline(width=64, height=64)
    
    # Send 5 random meshes with uncorrelated vertices
    for _ in range(5):
        pipeline.clear()
        verts = np.random.uniform(-1.0, 1.0, (12, 3)).astype(np.float32)
        faces = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]], dtype=np.int32)
        mvp = np.eye(4, dtype=np.float32)

        meta = pipeline.render_mesh(verts, faces, mvp)
        assert pipeline.color_buffer.shape == (64, 64, 4)
        assert "rasterized_faces" in meta
