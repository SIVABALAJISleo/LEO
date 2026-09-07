"""
tests/test_cbe_phase6.py
Unit tests for Reservoir, SpatiotemporalSampleReuse, RadianceCache, and SpatialReuseEngine.
"""

import numpy as np
import pytest

from cbe.reuse.reservoir import Reservoir, SamplePayload
from cbe.reuse.sample_reuse import SpatiotemporalSampleReuse
from cbe.reuse.radiance_reuse import RadianceCache
from cbe.reuse.spatial_reuse import SpatialReuseEngine


def test_reservoir_sampling_update_and_combine():
    r1 = Reservoir()
    cand1 = SamplePayload(np.array([0, 1, 0], dtype=np.float32), np.array([1, 1, 1], dtype=np.float32), 10.0, 0)
    cand2 = SamplePayload(np.array([1, 0, 0], dtype=np.float32), np.array([0.5, 0.5, 0.5], dtype=np.float32), 5.0, 1)
    
    r1.update(cand1, weight=1.0)
    r1.update(cand2, weight=2.0)
    assert r1.M == 2
    assert r1.w_sum == 3.0
    
    r1.finalize(target_pdf=1.0)
    assert r1.W > 0.0
    
    # Test combine
    r2 = Reservoir()
    r2.combine(r1, target_pdf=1.0)
    assert r2.M == 2


def test_radiance_cache_insertion_and_query():
    rc = RadianceCache(cell_size=0.10)
    pos = np.array([1.25, 2.05, 3.85], dtype=np.float32)
    normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    radiance = np.array([0.8, 0.6, 0.4], dtype=np.float32)
    
    # Initial query should miss
    rad, hit, conf = rc.query(pos, normal)
    assert hit is False
    
    # Insert sample
    rc.store(pos, normal, radiance)
    
    # Query should now hit
    rad, hit, conf = rc.query(pos, normal)
    assert hit is True
    assert conf > 0.8
    assert np.allclose(rad, radiance, atol=1e-3)


def test_spatiotemporal_sample_reuse():
    H, W = 16, 16
    reuse_engine = SpatiotemporalSampleReuse(height=H, width=W)
    
    normals = np.zeros((H, W, 3), dtype=np.float32)
    normals[..., 1] = 1.0  # Upwards surface
    depths = np.ones((H, W), dtype=np.float32) * 2.0
    mv = np.zeros((H, W, 2), dtype=np.float32)
    
    candidates = [
        SamplePayload(np.array([0, 1, 0], dtype=np.float32), np.array([1, 1, 1], dtype=np.float32), 10.0, 0),
        SamplePayload(np.array([0.707, 0.707, 0], dtype=np.float32), np.array([0.8, 0.8, 0.8], dtype=np.float32), 15.0, 1)
    ]
    
    irradiance = reuse_engine.resample(normals, depths, mv, candidates)
    assert irradiance.shape == (H, W, 3)
    assert np.any(irradiance > 0.0)


def test_spatial_reuse_filter():
    H, W = 16, 16
    color = np.zeros((H, W, 3), dtype=np.float32)
    # Put high-confidence bright color in center
    color[7:9, 7:9] = 1.0
    normals = np.zeros((H, W, 3), dtype=np.float32)
    normals[..., 1] = 1.0
    depths = np.ones((H, W), dtype=np.float32) * 5.0
    
    # Center has confidence 1.0, neighbors have 0.0
    confidence = np.zeros((H, W), dtype=np.float32)
    confidence[7:9, 7:9] = 1.0
    
    s_engine = SpatialReuseEngine(filter_radius=2)
    filtered = s_engine.filter_spatial(color, normals, depths, confidence)
    
    # Neighbors adjacent to center should receive propagated radiance
    assert filtered[6, 7, 0] > 0.0
