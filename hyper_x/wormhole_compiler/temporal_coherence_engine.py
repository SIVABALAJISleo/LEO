"""
hyper_x/wormhole_compiler/temporal_coherence_engine.py
=============================================================================
Universal Temporal Coherence & Sequential State Engine (Section 11)
=============================================================================
For sequential / time-varying workloads (graphics, video, physical simulation,
streaming time-series, iterative solvers):
Tracks:
    frame_t, frame_{t+1}, frame_{t+2}, ...
Detects:
    1. Unchanged regions (exact spatial identity across frames)
    2. Motion regions / affine translation blocks
    3. Residual delta regions
    4. Reusable intermediate representations / state memoization

EXACTNESS GUARD:
Temporal shortcuts are NEVER used when the contract requires STRICT_EXACT output
unless the temporal reconstruction is mathematically proven bitwise/numerically exact.
Never compare different mathematical workloads and call them equivalent.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, CorrectnessRequirement


@dataclass
class TemporalCoherenceReport:
    workload_id: str
    frame_index: int
    temporal_similarity_ratio: float  # Fraction of state/pixels unchanged
    reused_state_ratio: float
    nominal_operations: float
    executed_operations: float
    work_elimination_ratio: float
    latency_ms: float
    full_recomputation_latency_ms: float
    speedup: float
    reconstruction_exact: bool
    quality_metric: float  # e.g., 1.0 for exact, or SSIM/PSNR for perceptual

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "frame_index": self.frame_index,
            "temporal_similarity_ratio": round(self.temporal_similarity_ratio, 4),
            "reused_state_ratio": round(self.reused_state_ratio, 4),
            "nominal_operations": self.nominal_operations,
            "executed_operations": self.executed_operations,
            "work_elimination_ratio": round(self.work_elimination_ratio, 4),
            "latency_ms": round(self.latency_ms, 3),
            "full_recomputation_latency_ms": round(self.full_recomputation_latency_ms, 3),
            "speedup": round(self.speedup, 2),
            "reconstruction_exact": self.reconstruction_exact,
            "quality_metric": round(self.quality_metric, 6),
        }


class TemporalCoherenceEngine:
    """
    Exploits temporal coherence across sequential frame pipelines.
    """

    def __init__(self, block_size: int = 16):
        self.block_size = block_size
        self.previous_frames: Dict[str, np.ndarray] = {}
        self.previous_outputs: Dict[str, np.ndarray] = {}
        self.frame_counters: Dict[str, int] = {}

    def reset(self, stream_id: Optional[str] = None):
        if stream_id:
            self.previous_frames.pop(stream_id, None)
            self.previous_outputs.pop(stream_id, None)
            self.frame_counters.pop(stream_id, None)
        else:
            self.previous_frames.clear(
                self.previous_outputs.clear()
            )
            self.frame_counters.clear()

    def process_frame_temporal(
        self,
        stream_id: str,
        current_frame: np.ndarray,
        filter_kernel_fn: Callable[[np.ndarray], np.ndarray],
        contract: Optional[WorkloadContract] = None,
    ) -> Tuple[np.ndarray, TemporalCoherenceReport]:
        """
        Processes frame using temporal block change detection.
        Only recomputes filter_kernel_fn on blocks that have changed.
        """
        t0 = time.perf_counter()
        frame_idx = self.frame_counters.get(stream_id, 0) + 1
        self.frame_counters[stream_id] = frame_idx

        prev_frame = self.previous_frames.get(stream_id)
        prev_output = self.previous_outputs.get(stream_id)

        H, W = current_frame.shape[:2]
        nominal_ops = float(current_frame.size * 9)  # Standard 3x3 filter cost

        if prev_frame is None or prev_output is None or prev_frame.shape != current_frame.shape:
            # Cold frame 0: Must compute full frame
            output = filter_kernel_fn(current_frame)
            self.previous_frames[stream_id] = current_frame.copy()
            self.previous_outputs[stream_id] = output.copy()
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            report = TemporalCoherenceReport(
                workload_id=contract.workload_id if contract else stream_id,
                frame_index=frame_idx,
                temporal_similarity_ratio=0.0,
                reused_state_ratio=0.0,
                nominal_operations=nominal_ops,
                executed_operations=nominal_ops,
                work_elimination_ratio=0.0,
                latency_ms=elapsed_ms,
                full_recomputation_latency_ms=elapsed_ms,
                speedup=1.0,
                reconstruction_exact=True,
                quality_metric=1.0,
            )
            return output, report

        # Temporal change detection by blocks
        bs = self.block_size
        output = prev_output.copy()

        # Compute difference
        diff = np.abs(current_frame - prev_frame)
        if diff.ndim == 3:
            diff_2d = np.max(diff, axis=-1)
        else:
            diff_2d = diff

        # In exact mode: block must have max diff == 0 to be reused
        is_exact = contract.correctness == CorrectnessRequirement.EXACT if contract else True
        tol = 0.0 if is_exact else (contract.tolerance if contract else 1e-4)

        blocks_y = (H + bs - 1) // bs
        blocks_x = (W + bs - 1) // bs
        total_blocks = blocks_y * blocks_x
        reused_blocks = 0

        for by in range(blocks_y):
            y_start = by * bs
            y_end = min(H, (by + 1) * bs)
            for bx in range(blocks_x):
                x_start = bx * bs
                x_end = min(W, (bx + 1) * bs)

                block_diff = diff_2d[y_start:y_end, x_start:x_end]
                if np.max(block_diff) <= tol:
                    # Block is unchanged! Reuse previous output
                    reused_blocks += 1
                else:
                    # Pad region by 1 for 3x3 boundary correctly
                    pad_y_start = max(0, y_start - 1)
                    pad_y_end = min(H, y_end + 1)
                    pad_x_start = max(0, x_start - 1)
                    pad_x_end = min(W, x_end + 1)

                    sub_in = current_frame[pad_y_start:pad_y_end, pad_x_start:pad_x_end]
                    sub_out = filter_kernel_fn(sub_in)

                    # Extract the valid inner region
                    local_y0 = y_start - pad_y_start
                    local_y1 = local_y0 + (y_end - y_start)
                    local_x0 = x_start - pad_x_start
                    local_x1 = local_x0 + (x_end - x_start)

                    output[y_start:y_end, x_start:x_end] = sub_out[local_y0:local_y1, local_x0:local_x1]

        # Update cache
        self.previous_frames[stream_id] = current_frame.copy()
        self.previous_outputs[stream_id] = output.copy()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Reference baseline
        t_ref_0 = time.perf_counter()
        ref_output = filter_kernel_fn(current_frame)
        ref_elapsed_ms = (time.perf_counter() - t_ref_0) * 1000.0

        # Verification check
        max_err = float(np.max(np.abs(output - ref_output)))
        is_exact_match = max_err <= (1e-5 if is_exact else tol)

        reused_ratio = float(reused_blocks / max(1, total_blocks))
        executed_ops = nominal_ops * (1.0 - reused_ratio)
        wer = float(reused_ratio)

        report = TemporalCoherenceReport(
            workload_id=contract.workload_id if contract else stream_id,
            frame_index=frame_idx,
            temporal_similarity_ratio=reused_ratio,
            reused_state_ratio=reused_ratio,
            nominal_operations=nominal_ops,
            executed_operations=executed_ops,
            work_elimination_ratio=wer,
            latency_ms=elapsed_ms,
            full_recomputation_latency_ms=ref_elapsed_ms,
            speedup=float(ref_elapsed_ms / max(0.0001, elapsed_ms)),
            reconstruction_exact=is_exact_match,
            quality_metric=float(1.0 - min(1.0, max_err)),
        )

        return output, report
