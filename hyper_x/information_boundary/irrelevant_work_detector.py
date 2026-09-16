#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/irrelevant_work_detector.py
========================================================
Phase 3: Irrelevant Work Detector.
Identifies and flags operations that consume energy and time but produce zero observable impact:
  1. Culled geometric / viewport elements
  2. Inactive neural activation dead zones (e.g. ReLU zeros)
  3. Unobserved logit dimensions when only top-1 / argmax is required
  4. Spatial grid cells outside stencil domain of influence
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Set
import numpy as np


class IrrelevantWorkDetector:
    """
    Scans workload intermediate states and dependency subgraphs for provably irrelevant computation.
    """

    @staticmethod
    def detect_spatial_culled(
        bounding_boxes: np.ndarray,  # Shape (N, 4): [x_min, y_min, x_max, y_max]
        viewport: Tuple[float, float, float, float] = (0.0, 0.0, 1920.0, 1080.0)
    ) -> Dict[str, Any]:
        """Identifies primitives strictly outside the rendering viewport."""
        vx0, vy0, vx1, vy1 = viewport
        x0, y0, x1, y1 = bounding_boxes[:, 0], bounding_boxes[:, 1], bounding_boxes[:, 2], bounding_boxes[:, 3]

        outside = (x1 < vx0) | (x0 > vx1) | (y1 < vy0) | (y0 > vy1)
        culled_indices = np.where(outside)[0]
        visible_indices = np.where(~outside)[0]

        total = len(bounding_boxes)
        culled = len(culled_indices)

        return {
            "total_primitives": total,
            "culled_primitives": culled,
            "visible_primitives": len(visible_indices),
            "culled_ratio": culled / max(total, 1),
            "culled_indices": culled_indices.tolist(),
            "visible_indices": visible_indices.tolist(),
        }

    @staticmethod
    def detect_activation_sparsity(
        activations: np.ndarray,
        dead_threshold: float = 1e-6
    ) -> Dict[str, Any]:
        """Detects inactive neural activations (e.g., ReLU zeroes or low magnitude values)."""
        flat = activations.reshape(-1)
        total = flat.size
        zero_mask = np.abs(flat) <= dead_threshold
        dead_count = int(np.sum(zero_mask))

        return {
            "total_activations": total,
            "inactive_activations": dead_count,
            "active_activations": total - dead_count,
            "sparsity_ratio": dead_count / max(total, 1),
            "is_highly_sparse": (dead_count / max(total, 1)) > 0.50,
        }

    @staticmethod
    def detect_unobserved_logits(
        vocab_size: int,
        k: int = 1
    ) -> Dict[str, Any]:
        """Calculates unobserved logits when only top-k / argmax is required by contract."""
        unobserved = max(0, vocab_size - k)
        return {
            "total_vocab": vocab_size,
            "observed_k": k,
            "unobserved_tokens": unobserved,
            "unobserved_ratio": unobserved / max(vocab_size, 1),
            "allow_hierarchical_reduction": vocab_size > 1024 and k <= 5,
        }
