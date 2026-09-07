"""
cbe/prediction: Lightweight forward prediction engine.
Predicts camera trajectories, object kinematics, occlusions, and workload demand
to enable zero-latency predictive precomputation.
"""

from .motion_predictor import MotionPredictor
from .visibility_predictor import VisibilityPredictor
from .lighting_predictor import LightingPredictor
from .workload_predictor import WorkloadPredictor
from .frame_predictor import FramePredictor, PredictedFrameState

__all__ = [
    "MotionPredictor",
    "VisibilityPredictor",
    "LightingPredictor",
    "WorkloadPredictor",
    "FramePredictor",
    "PredictedFrameState",
]
