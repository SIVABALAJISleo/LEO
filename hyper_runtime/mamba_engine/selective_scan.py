import numpy as np
from .ssm_state import SSMState

class SelectiveScanKernel:
    """
    Simulates the core selective scan operation of Mamba.
    Instead of attending to all previous tokens (O(N^2) time), it compresses
    the context into the state sequentially: h_t = A_t * h_{t-1} + B_t * x_t.
    """
    def __init__(self, hidden_dim: int, state_dim: int):
        self.hidden_dim = hidden_dim
        self.state_dim = state_dim
        
    def forward_step(self, x_t: np.ndarray, dt: np.ndarray, A: np.ndarray, B_t: np.ndarray, C_t: np.ndarray, state: SSMState) -> np.ndarray:
        """
        Executes a single step of the selective state space model.
        x_t: [batch, hidden_dim]
        dt: [batch, hidden_dim] (step size, input-dependent)
        A: [hidden_dim, state_dim] (transition matrix, usually fixed)
        B_t: [batch, state_dim] (input matrix, input-dependent)
        C_t: [batch, state_dim] (output matrix, input-dependent)
        """
        # Get previous state
        h_prev = state.get_state() # [batch, hidden_dim, state_dim]
        
        # 1. Discretize A and B (Simulated zero-order hold)
        # dA_t = exp(dt * A)
        # Using a simple Taylor approximation for the simulation: dA_t = 1 + dt * A
        # Reshape for broadcasting
        dt_expanded = np.expand_dims(dt, axis=-1) # [batch, hidden_dim, 1]
        A_expanded = np.expand_dims(A, axis=0) # [1, hidden_dim, state_dim]
        
        dA_t = 1.0 + dt_expanded * A_expanded # [batch, hidden_dim, state_dim]
        
        # dB_t = dt * B_t
        B_expanded = np.expand_dims(B_t, axis=1) # [batch, 1, state_dim]
        dB_t = dt_expanded * B_expanded # [batch, hidden_dim, state_dim]
        
        # 2. Update state: h_t = dA_t * h_{t-1} + dB_t * x_t
        x_expanded = np.expand_dims(x_t, axis=-1) # [batch, hidden_dim, 1]
        h_t = dA_t * h_prev + dB_t * x_expanded # [batch, hidden_dim, state_dim]
        
        state.update_state(h_t)
        
        # 3. Compute output: y_t = C_t * h_t
        C_expanded = np.expand_dims(C_t, axis=1) # [batch, 1, state_dim]
        # Sum over state dimension
        y_t = np.sum(h_t * C_expanded, axis=-1) # [batch, hidden_dim]
        
        return y_t
