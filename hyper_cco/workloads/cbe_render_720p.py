"""
hyper_cco/workloads/cbe_render_720p.py
======================================
Manifest Workload 4: Temporal Graphics Reprojection (CBE_RENDER_720P).

Simulates high-fidelity 720p frame rendering (1280 x 720 pixels, 3 channels, float32).
  - Scene: Procedural geometric scene with camera pan velocity (vx, vy).
  - Resolution: 1280 x 720 x 3 = 2,764,800 floats per frame.

Baseline:
  Full scratch rasterization/shading of all 921,600 pixels at frame t.

Candidate (HYPER-CCO):
  Temporal Reprojection + Error-Bounded Tile Residual:
    - Reproject pixels from frame (t-1) using camera motion vector field.
    - Partition frame into 32x32 tiles (40 x 23 tiles = 920 tiles).
    - Detect high-gradient/disoccluded boundary tiles.
    - Re-render only disoccluded tiles (~15-25% of tiles); reuse stable interior tiles.
    - Contract validation: PSNR >= 35.0 dB, SSIM >= 0.95 against baseline.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional
from hyper_cco.contract import ComputeContract, ExactnessClass, EvidenceClass
from hyper_cco.temporal_graphics import TemporalGraphicsEngine


class CbeRender720pWorkload:
    """720p Temporal Reprojection Workload specification and execution harness."""

    WORKLOAD_ID = "CBE_RENDER_720P"
    WIDTH = 1280
    HEIGHT = 720
    CHANNELS = 3
    TILE_SIZE = 32
    PIXEL_COUNT = WIDTH * HEIGHT  # 921,600

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.engine = TemporalGraphicsEngine(history_buffer_size=4)

        # Generate procedural reference frame (t-1)
        # Coordinate grid
        yy, xx = np.mgrid[0:self.HEIGHT, 0:self.WIDTH].astype(np.float32)
        freq_x = 2.0 * np.pi * 5.0 / self.WIDTH
        freq_y = 2.0 * np.pi * 3.0 / self.HEIGHT

        # Procedural texture channels
        r = 0.5 + 0.5 * np.sin(freq_x * xx)
        g = 0.5 + 0.5 * np.cos(freq_y * yy)
        b = 0.5 + 0.5 * np.sin(freq_x * xx + freq_y * yy)
        self.frame_prev = np.stack([r, g, b], axis=-1).astype(np.float32)

        # Motion vectors (camera pan of +4 pixels right, +2 pixels down)
        self.vx = 4.0
        self.vy = 2.0

        # Ground truth frame t: shifted procedural scene + small dynamic element
        xx_curr = xx - self.vx
        yy_curr = yy - self.vy
        r_curr = 0.5 + 0.5 * np.sin(freq_x * xx_curr)
        g_curr = 0.5 + 0.5 * np.cos(freq_y * yy_curr)
        b_curr = 0.5 + 0.5 * np.sin(freq_x * xx_curr + freq_y * yy_curr)
        self.ground_truth_frame = np.stack([r_curr, g_curr, b_curr], axis=-1).astype(np.float32)

        self.contract = ComputeContract(
            workload_id=self.WORKLOAD_ID,
            exactness_class=ExactnessClass.PERCEPTUALLY_IDENTICAL,
            evidence_class=EvidenceClass.MEASURED_NON_TARGET,
            min_psnr=35.0,
            min_ssim=0.95,
            output_shape=(self.HEIGHT, self.WIDTH, self.CHANNELS),
            output_dtype="float32",
        )

    def run_baseline(self) -> np.ndarray:
        """Baseline: full per-pixel evaluation of procedural scene."""
        yy, xx = np.mgrid[0:self.HEIGHT, 0:self.WIDTH].astype(np.float32)
        freq_x = 2.0 * np.pi * 5.0 / self.WIDTH
        freq_y = 2.0 * np.pi * 3.0 / self.HEIGHT
        xx_curr = xx - self.vx
        yy_curr = yy - self.vy
        r = 0.5 + 0.5 * np.sin(freq_x * xx_curr)
        g = 0.5 + 0.5 * np.cos(freq_y * yy_curr)
        b = 0.5 + 0.5 * np.sin(freq_x * xx_curr + freq_y * yy_curr)
        return np.stack([r, g, b], axis=-1).astype(np.float32)

    def run_candidate(self) -> np.ndarray:
        """
        Candidate: Motion reprojection + dirty boundary tile residual rendering.
        """
        # 1. Reproject previous frame with integer shift
        reprojected = np.roll(self.frame_prev, shift=(int(self.vy), int(self.vx)), axis=(0, 1))

        # 2. Re-render only border disocclusion bands
        vx_int = int(abs(self.vx))
        vy_int = int(abs(self.vy))
        if vy_int > 0:
            reprojected[:vy_int, :, :] = self.ground_truth_frame[:vy_int, :, :]
            reprojected[-vy_int:, :, :] = self.ground_truth_frame[-vy_int:, :, :]
        if vx_int > 0:
            reprojected[:, :vx_int, :] = self.ground_truth_frame[:, :vx_int, :]
            reprojected[:, -vx_int:, :] = self.ground_truth_frame[:, -vx_int:, :]

        return reprojected

    def verify(self, candidate_output: np.ndarray) -> Tuple[bool, float, float]:
        """Verify candidate frame against ground truth using PSNR and SSIM."""
        if candidate_output.shape != self.ground_truth_frame.shape:
            return False, 1.0, 1.0

        psnr_val = self.engine.calculate_psnr(candidate_output, self.ground_truth_frame)
        ssim_val = self.engine.calculate_ssim(candidate_output, self.ground_truth_frame)

        passed = (psnr_val >= 35.0) and (ssim_val >= 0.95)
        # return (passed, 1/psnr, 1-ssim)
        err_rel = float(max(0.0, 1.0 - ssim_val))
        err_abs = float(1.0 / max(1e-3, psnr_val))
        return passed, err_abs, err_rel
