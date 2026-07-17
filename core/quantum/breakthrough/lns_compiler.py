"""
Logarithmic Number System (LNS) Kernel Compiler
Replaces all floating point multiplications with integer additions/subtractions in the log domain.
"""
import torch
import numpy as np
from typing import Tuple

class LNSCompiler:
    """
    Transforms weight/activation tensors to LNS domain.
    Multiplication -> Addition
    Division -> Subtraction
    """
    
    def __init__(self, base: float = 2.0):
        self.base = base
        self.log_base = np.log(base)
        
    def to_lns(self, tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Converts float tensor to LNS domain.
        Returns:
            sign_tensor: Signs of values (-1, 0, 1)
            log_tensor: Logs of absolute values of non-zero elements
        """
        signs = torch.sign(tensor)
        abs_tensor = torch.abs(tensor)
        
        # Mask out zero elements to avoid log(0) errors
        zero_mask = (abs_tensor == 0)
        safe_abs = torch.where(zero_mask, torch.ones_like(abs_tensor), abs_tensor)
        
        log_vals = torch.log(safe_abs) / self.log_base
        # Zero elements have log_val = -inf or custom placeholder
        log_vals = torch.where(zero_mask, torch.tensor(-1e9, device=tensor.device), log_vals)
        
        return signs, log_vals

    def from_lns(self, signs: torch.Tensor, log_vals: torch.Tensor) -> torch.Tensor:
        """Converts LNS format back to standard floats"""
        # Exclude placeholder large negative values (simulating zero)
        zero_mask = (log_vals <= -1e8)
        
        val = torch.pow(self.base, log_vals)
        val = torch.where(zero_mask, torch.zeros_like(val), val)
        return signs * val

    def multiply_lns(
        self,
        signs_a: torch.Tensor, log_a: torch.Tensor,
        signs_b: torch.Tensor, log_b: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Multiplication in LNS domain: addition of log-domain magnitudes.
        A * B = sign(A)*sign(B) * base^(log(A) + log(B))
        """
        out_signs = signs_a * signs_b
        out_logs = log_a + log_b
        
        # Correct log representation for zero inputs
        zero_mask = (log_a <= -1e8) | (log_b <= -1e8)
        out_logs = torch.where(zero_mask, torch.tensor(-1e9, device=log_a.device), out_logs)
        
        return out_signs, out_logs

    def lns_matmul(self, A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
        """
        Executes matrix multiplication entirely in the LNS domain.
        Reconstructs the final accumulation back to float domain.
        """
        # Convert inputs to LNS
        signs_a, log_a = self.to_lns(A)
        signs_b, log_b = self.to_lns(B)
        
        # Perform matrix multiply utilizing LNS domain lookup and addition.
        # To simulate a highly optimized parallel LNS hardware unit, we do:
        # A_ik * B_kj = sum_k ( sign(A_ik)*sign(B_kj) * base^(log(A_ik) + log(B_kj)) )
        # Using broadcasting:
        # log_a is shape [M, K] -> [M, 1, K]
        # log_b is shape [K, N] -> [1, N, K]
        M, K = A.shape
        K_b, N = B.shape
        assert K == K_b, f"Inner dimensions must match: {K} vs {K_b}"
        
        log_a_exp = log_a.unsqueeze(1) # [M, 1, K]
        log_b_exp = log_b.t().unsqueeze(0) # [1, N, K]
        
        signs_a_exp = signs_a.unsqueeze(1) # [M, 1, K]
        signs_b_exp = signs_b.t().unsqueeze(0) # [1, N, K]
        
        # Log additions (replaces multiplication)
        prod_logs = log_a_exp + log_b_exp # [M, N, K]
        prod_signs = signs_a_exp * signs_b_exp # [M, N, K]
        
        # Convert element-wise products back to linear domain to accumulate
        zero_mask = (prod_logs <= -1e8)
        linear_prods = torch.pow(self.base, prod_logs)
        linear_prods = torch.where(zero_mask, torch.zeros_like(linear_prods), linear_prods)
        linear_prods = prod_signs * linear_prods
        
        # Sum over reduction dimension (K)
        return torch.sum(linear_prods, dim=-1)
