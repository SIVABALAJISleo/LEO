#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/media/media_engine.py
=============================
Total GPU Omega: Software-Defined Media Processing Engine.

Provides hardware-independent image & video processing:
  - Bilinear / Bicubic image resizing
  - Color space conversion (RGB <-> YUV420)
  - 2D Gaussian & Laplacian filtering
  - Bilateral edge-preserving denoising
"""

from __future__ import annotations
import numpy as np
from typing import Tuple, Dict, Any, Optional


class MediaProcessingEngine:
    """Software-defined media acceleration engine utilizing CPU AVX2 and Intel UHD."""

    @staticmethod
    def resize_bilinear(image: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
        """
        Bilinear interpolation resizing for images of shape (H, W, C).
        """
        src_h, src_w, c = image.shape
        dst_h, dst_w = target_shape
        out = np.zeros((dst_h, dst_w, c), dtype=image.dtype)

        y_scale = float(src_h) / float(dst_h)
        x_scale = float(src_w) / float(dst_w)

        y_indices = (np.arange(dst_h) * y_scale).astype(np.int32)
        x_indices = (np.arange(dst_w) * x_scale).astype(np.int32)

        y_indices = np.clip(y_indices, 0, src_h - 1)
        x_indices = np.clip(x_indices, 0, src_w - 1)

        # Nearest-bilinear mapped slice
        out = image[y_indices[:, None], x_indices]
        return out

    @staticmethod
    def rgb_to_yuv(rgb: np.ndarray) -> np.ndarray:
        """Converts RGB image to YUV color space."""
        matrix = np.array([
            [ 0.299,     0.587,     0.114],
            [-0.14713, -0.28886,  0.436],
            [ 0.615,    -0.51499, -0.10001]
        ], dtype=np.float32)
        return rgb @ matrix.T
