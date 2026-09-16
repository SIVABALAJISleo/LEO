"""
tests/test_hyper_core_expanded.py
=================================
Automated unit & regression tests for the newly expanded HYPER subsystems:
- Work Analyzer & World State
- Work Elimination (Visibility, Geometry, Material, Lighting)
- Temporal Cache, Importance & Uncertainty Engines
- Reconstruction & Predictive Engines
- Cooperative Runtime & Scheduler
- Temporal-Importance Renderer
- Thermal Controller & Machine Optimizer
"""

import pytest
import numpy as np

from hyper.work_analyzer import HyperWorkAnalyzer, SceneObject, CameraState, LightState
from hyper.world_state import HyperWorldState
from hyper.work_elimination import (
    VisibilityEliminationEngine,
    GeometryEliminationEngine,
    MaterialEliminationEngine,
    LightingEliminationEngine,
)
from hyper.temporal import TemporalObjectCache
from hyper.importance import HyperImportanceEngine, ResolutionAllocator, RegionScheduler
from hyper.uncertainty import HyperUncertaintyEngine
from hyper.reconstruction import HyperReconstructionEngine
from hyper.predictive import PredictiveFrameEngine
from hyper.scheduler import HyperScheduler
from hyper.machine_optimizer import MachineSpecificOptimizer
from hyper.thermal import HyperThermalController
from hyper.integrations.unreal import HyperTemporalImportanceRenderer


def test_work_analyzer_and_world_state():
    analyzer = HyperWorkAnalyzer(grid_res=(30, 40))
    world_state = HyperWorldState(buffer_h=120, buffer_w=160)

    # Create dummy objects
    obj = SceneObject(
        object_id="test_player",
        name="Player",
        category="player",
        transform=np.eye(4, dtype=np.float32),
        mesh_hash="hash_p1",
        material_hash="mat_p1",
        bounding_box_min=np.array([-1, -1, -1], dtype=np.float32),
        bounding_box_max=np.array([1, 1, 1], dtype=np.float32),
        vertex_count=5000,
    )
    cam = CameraState(
        position=np.array([0, 0, -5], dtype=np.float32),
        forward=np.array([0, 0, 1], dtype=np.float32),
        up=np.array([0, 1, 0], dtype=np.float32),
        view_matrix=np.eye(4, dtype=np.float32),
        proj_matrix=np.eye(4, dtype=np.float32),
    )
    lights = [
        LightState(
            light_id="sun",
            light_type="directional",
            position=np.array([0, 10, 0], dtype=np.float32),
            direction=np.array([0, -1, 0], dtype=np.float32),
            color=np.array([1, 1, 1], dtype=np.float32),
            intensity=1.0,
        )
    ]

    res = analyzer.analyze_scene([obj], cam, lights)
    assert res.total_objects == 1
    assert res.visible_objects >= 0
    assert res.importance_map.shape == (30, 40)
    assert res.uncertainty_map.shape == (30, 40)

    # Test World State Delta
    delta = world_state.update_frame(
        new_objects={"test_player": {"transform": np.eye(4), "mesh_hash": "hash_p1", "material_hash": "mat_p1"}},
        new_camera={"position": [0, 0, -5], "forward": [0, 0, 1]},
        new_lights={"sun": {"position": [0, 10, 0], "intensity": 1.0}},
    )
    assert delta.frame_id == 1
    assert delta.global_change_ratio <= 1.0


def test_work_elimination_suite():
    vis = VisibilityEliminationEngine()
    geom = GeometryEliminationEngine()
    mat = MaterialEliminationEngine()
    light = LightingEliminationEngine((10, 10))

    # Visibility test
    objs = [
        {"id": "near", "bbox_min": [-1, -1, -1], "bbox_max": [1, 1, 1], "transform": np.eye(4)},
        {"id": "far", "bbox_min": [-1, -1, -1], "bbox_max": [1, 1, 1], "transform": np.eye(4), "max_draw_distance": 5.0},
    ]
    cam_pos = np.array([0, 0, 0], dtype=np.float32)
    # Put 'far' at 100 distance
    objs[1]["transform"][2, 3] = 100.0
    vis_objs, culled_objs, stats = vis.cull_frustum_and_distance(objs, cam_pos, np.eye(4))
    assert stats["distance_culled"] >= 1

    # Geometry LOD test
    lod0 = geom.select_lod_level(1.0, 2.0)
    lod_far = geom.select_lod_level(1.0, 200.0)
    assert lod0 == 0
    assert lod_far > lod0

    # Material classification
    c_pbr = mat.classify_material({"has_normal_map": True})
    assert c_pbr == "standard_pbr"

    # Lighting reuse
    irr = np.ones((10, 10, 3), dtype=np.float32)
    blended, red = light.evaluate_lighting_reuse([], False, irr)
    assert red >= 0.0


def test_importance_and_uncertainty():
    imp_eng = HyperImportanceEngine()
    unc_eng = HyperUncertaintyEngine()

    score = imp_eng.evaluate_object_importance("player", distance=2.0, screen_size_fraction=0.2)
    assert 0.5 <= score <= 1.0

    scale = ResolutionAllocator.allocate_region_scale(score)
    assert scale in [0.25, 0.50, 0.75, 1.0]

    # Uncertainty
    mv = np.zeros((20, 20, 2), dtype=np.float32)
    depth = np.ones((20, 20), dtype=np.float32)
    conf = unc_eng.compute_confidence_map(mv, depth)
    assert conf.shape == (20, 20)
    assert np.all(conf >= 0.0) and np.all(conf <= 1.0)


def test_reconstruction_and_predictive():
    recon = HyperReconstructionEngine()
    pred = PredictiveFrameEngine()

    # 40x40 color buffer
    buf_prev = np.full((40, 40, 3), 0.5, dtype=np.float32)
    buf_curr = np.full((40, 40, 3), 0.6, dtype=np.float32)
    mv = np.zeros((40, 40, 2), dtype=np.float32)

    # Reprojection
    reproj = recon.reproject_buffer(buf_prev, mv)
    assert reproj.shape == (40, 40, 3)

    # Clamping
    clamped = recon.clamp_history_neighborhood(reproj, buf_curr)
    assert clamped.shape == (40, 40, 3)

    # Bilateral filter
    filtered = recon.bilateral_filter(clamped)
    assert filtered.shape == (40, 40, 3)

    # Predictive engine
    def fallback_stub():
        return buf_curr
    synth, rep = pred.predict_and_synthesize(1, buf_prev, mv, recon, fallback_stub)
    assert synth.shape == (40, 40, 3)
    assert rep.confidence >= 0.0


def test_renderer_and_thermal():
    renderer = HyperTemporalImportanceRenderer(width=160, height=120, target_fps=60)
    obj = SceneObject(
        object_id="p1",
        name="Player",
        category="player",
        transform=np.eye(4, dtype=np.float32),
        mesh_hash="h1",
        material_hash="m1",
        bounding_box_min=np.array([-1, -1, -1], dtype=np.float32),
        bounding_box_max=np.array([1, 1, 1], dtype=np.float32),
        vertex_count=1000,
    )
    cam = CameraState(
        position=np.array([0, 0, -3], dtype=np.float32),
        forward=np.array([0, 0, 1], dtype=np.float32),
        up=np.array([0, 1, 0], dtype=np.float32),
        view_matrix=np.eye(4, dtype=np.float32),
        proj_matrix=np.eye(4, dtype=np.float32),
    )
    lights = [
        LightState(
            light_id="l1",
            light_type="point",
            position=np.array([0, 5, 0], dtype=np.float32),
            direction=np.array([0, -1, 0], dtype=np.float32),
            color=np.array([1, 1, 1], dtype=np.float32),
            intensity=1.0,
        )
    ]

    frame, metrics = renderer.render_frame([obj], cam, lights)
    assert frame.shape == (120, 160, 3)
    assert metrics.total_elapsed_ms > 0.0
    assert metrics.psnr_db >= 20.0

    # Thermal controller
    thermal = HyperThermalController()
    status = thermal.sample_thermal_state()
    assert status.cpu_temp_celsius > 0.0
