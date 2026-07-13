"""
Activation Sparsity Engine (ASE).
Dynamically predicts and skips zero-activation neurons before the matrix multiply.
"""
import numpy as np
from typing import Dict

from core.ira.shared.config import ASEConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector

class ActivationSparsityEngine:
    def __init__(self, config: ASEConfig = None):
        self.config = config or ASEConfig()
        
        self.layer_sparsity_history: Dict[int, list] = {}
        self.adaptive_thresholds: Dict[int, float] = {}
        
        self.logger = IRALogger.get_logger("ase")
        self.metrics = get_metric_collector().system.get_or_create_pillar("ase")

    def predict_activation_mask(self, input_activation: np.ndarray, layer_idx: int) -> np.ndarray:
        if layer_idx not in self.adaptive_thresholds:
            self.adaptive_thresholds[layer_idx] = self.config.sparsity_threshold
            
        threshold = self.adaptive_thresholds[layer_idx]
        
        # Simple heuristic: |input| > threshold -> likely active
        # Real implementations might use a small predictor network here
        mask = np.abs(input_activation) > threshold
        return mask

    def sparse_matmul(self, input_vec: np.ndarray, weight_matrix: np.ndarray,
                      bias: np.ndarray, layer_idx: int) -> np.ndarray:
        if not self.config.enable_sparse_forward:
            return self.full_matmul(input_vec, weight_matrix, bias)
            
        mask = self.predict_activation_mask(input_vec, layer_idx)
        
        # Extract active columns/elements
        # This assumes weight_matrix is (in_features, out_features)
        W_active = weight_matrix[:, mask]
        b_active = bias[mask]
        
        partial = input_vec @ W_active + b_active
        partial = np.maximum(0, partial)  # ReLU
        
        output = np.zeros(weight_matrix.shape[1], dtype=input_vec.dtype)
        output[mask] = partial
        
        if self.config.track_layer_sparsity:
            self.record_actual_sparsity(layer_idx, output)
            
        return output

    def full_matmul(self, input_vec: np.ndarray, weight_matrix: np.ndarray,
                    bias: np.ndarray) -> np.ndarray:
        output = input_vec @ weight_matrix + bias
        return np.maximum(0, output)

    def update_adaptive_threshold(self, layer_idx: int, actual_sparsity: float) -> None:
        if not self.config.adaptive_threshold:
            return
            
        if layer_idx not in self.adaptive_thresholds:
            self.adaptive_thresholds[layer_idx] = self.config.sparsity_threshold
            
        current = self.adaptive_thresholds[layer_idx]
        
        # If very sparse (>85%), increase threshold to skip even more safely
        # If dense (<50%), decrease threshold to not skip important features
        adjustment = 0.0
        if actual_sparsity > 0.85:
            adjustment = 0.05
        elif actual_sparsity < 0.5:
            adjustment = -0.05
            
        # Exponential moving average
        new_thresh = (self.config.threshold_decay * current) + ((1.0 - self.config.threshold_decay) * adjustment)
        new_thresh = max(0.01, min(0.5, new_thresh)) # Clamp
        
        self.adaptive_thresholds[layer_idx] = new_thresh

    def record_actual_sparsity(self, layer_idx: int, activation: np.ndarray) -> float:
        sparsity = 1.0 - (np.count_nonzero(activation) / max(1, activation.size))
        
        if layer_idx not in self.layer_sparsity_history:
            self.layer_sparsity_history[layer_idx] = []
            
        self.layer_sparsity_history[layer_idx].append(sparsity)
        
        # Keep recent history manageable
        if len(self.layer_sparsity_history[layer_idx]) > self.config.max_tracked_layers:
            self.layer_sparsity_history[layer_idx] = self.layer_sparsity_history[layer_idx][-self.config.max_tracked_layers:]
            
        self.update_adaptive_threshold(layer_idx, sparsity)
        return sparsity

    def get_average_sparsity(self, layer_idx: int = None) -> float:
        if layer_idx is not None:
            hist = self.layer_sparsity_history.get(layer_idx, [])
            return sum(hist) / max(1, len(hist))
            
        all_sparsities = []
        for hist in self.layer_sparsity_history.values():
            if hist:
                all_sparsities.append(sum(hist) / len(hist))
                
        return sum(all_sparsities) / max(1, len(all_sparsities))

    def get_sparsity_report(self) -> dict:
        report = {}
        for idx, hist in self.layer_sparsity_history.items():
            if hist:
                report[f"layer_{idx}"] = {
                    "min": min(hist),
                    "max": max(hist),
                    "mean": sum(hist) / len(hist),
                    "threshold": self.adaptive_thresholds.get(idx, self.config.sparsity_threshold)
                }
        return report

    def reset_stats(self) -> None:
        self.layer_sparsity_history.clear()
        self.adaptive_thresholds.clear()
