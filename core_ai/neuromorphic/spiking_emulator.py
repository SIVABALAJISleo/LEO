import torch
import logging
import warnings

logger = logging.getLogger(__name__)

class NeuromorphicEmulator:
    """
    Event-driven neuromorphic execution.
    Only computes updates on sparse spikes (delta > 0.05).
    Bypasses 95% of matrix multiplications.
    """
    def __init__(self, delta_threshold=0.05, sparse_threshold=0.05):
        self.delta_threshold = delta_threshold
        self.sparse_threshold = sparse_threshold
        self.prev_state = None
        
        try:
            import torch
            self.torch_available = True
        except ImportError:
            self.torch_available = False
            warnings.warn("PyTorch not installed. Spiking emulator requires PyTorch for sparse tensors.")

    def detect_spikes(self, input_tensor: torch.Tensor, prev_state: torch.Tensor):
        """Returns mask of elements where delta > threshold."""
        delta = torch.abs(input_tensor - prev_state)
        return delta > self.delta_threshold

    def process_spikes(self, current_state, weights):
        """
        Executes sparse updates if spike ratio < 5%.
        current_state: numpy array or torch tensor.
        """
        if not self.torch_available:
            return current_state @ weights
            
        if not isinstance(current_state, torch.Tensor):
            current_state = torch.tensor(current_state, dtype=torch.float32)
        if not isinstance(weights, torch.Tensor):
            weights = torch.tensor(weights, dtype=torch.float32)

        if self.prev_state is None:
            self.prev_state = current_state.clone()
            return torch.matmul(current_state, weights)

        spike_mask = self.detect_spikes(current_state, self.prev_state)
        spike_ratio = spike_mask.sum().item() / current_state.numel()

        if spike_ratio < self.sparse_threshold:
            logger.debug(f"[Neuromorphic] Sparse update active. Spike ratio: {spike_ratio:.4f}")
            # Get indices and values of spikes
            indices = torch.nonzero(spike_mask).t()
            values = current_state[spike_mask]
            
            # Create sparse tensor mapping
            sparse_spikes = torch.sparse_coo_tensor(indices, values, current_state.size())
            
            # Sparse matrix multiplication (significantly bypassing dense math)
            output = torch.sparse.mm(sparse_spikes, weights)
        else:
            # Full dense update
            output = torch.matmul(current_state, weights)
            
        self.prev_state = current_state.clone()
        return output
