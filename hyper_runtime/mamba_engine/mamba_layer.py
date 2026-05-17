import numpy as np
import logging
from .ssm_state import SSMState
from .selective_scan import SelectiveScanKernel

logger = logging.getLogger("HyperCore.MambaLayer")

class MambaLayer:
    """
    HyperCore MODULE 10 — Mamba Engine (State Space Layer)
    
    Replaces Transformers for long-context tasks. 
    Memory footprint scales O(1) with sequence length instead of O(N^2).
    """
    def __init__(self, d_model: int = 2048, d_state: int = 16, expand: int = 2):
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = int(expand * d_model)
        
        # Mamba requires projecting x to B, C, and dt (step size)
        # Mock projection weights
        self.proj_B = np.random.randn(self.d_inner, d_state).astype(np.float32) * 0.02
        self.proj_C = np.random.randn(self.d_inner, d_state).astype(np.float32) * 0.02
        self.proj_dt = np.random.randn(self.d_inner, self.d_inner).astype(np.float32) * 0.02
        
        # Transition matrix A (often initialized to negative powers of a base)
        self.A = -np.exp(np.random.randn(self.d_inner, d_state).astype(np.float32))
        
        self.scan_kernel = SelectiveScanKernel(self.d_inner, d_state)
        logger.info(f"MambaLayer initialized with d_model={d_model}, d_state={d_state}.")

    def forward_sequence(self, x_seq: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Executes the Mamba block over a sequence of tokens.
        x_seq: [batch, seq_len, d_inner]
        Returns the output sequence and telemetry metrics.
        """
        batch, seq_len, _ = x_seq.shape
        
        # Initialize state for this batch
        state = SSMState(batch, self.d_inner, self.d_state)
        
        out_seq = np.zeros_like(x_seq)
        
        # In a real hardware-optimized Mamba kernel, this loop is parallelized
        # using a parallel scan (prefix sum) algorithm. We simulate the logic sequentially.
        for t in range(seq_len):
            x_t = x_seq[:, t, :]
            
            # Input-dependent projections
            B_t = np.dot(x_t, self.proj_B) # [batch, d_state]
            C_t = np.dot(x_t, self.proj_C) # [batch, d_state]
            dt_raw = np.dot(x_t, self.proj_dt)
            # Softplus for dt to keep it positive
            dt = np.log1p(np.exp(np.clip(dt_raw, -20, 20))) # [batch, d_inner]
            
            # Step the scan kernel
            y_t = self.scan_kernel.forward_step(x_t, dt, self.A, B_t, C_t, state)
            out_seq[:, t, :] = y_t
            
        metrics = {
            "seq_len": seq_len,
            "ssm_state_mb": state.get_memory_footprint_mb(),
            "transformer_kv_equivalent_mb": (batch * seq_len * self.d_inner * 2 * 4) / (1024 * 1024)
        }
        
        return out_seq, metrics
