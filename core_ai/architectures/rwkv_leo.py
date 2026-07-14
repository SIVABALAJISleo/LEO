import torch
import torch.nn as nn
import torch.nn.functional as F

class RWKVLeo(nn.Module):
    """
    RWKV (Receptance Weighted Key Value) Linear Attention Block.
    Provides Transformer-like performance with RNN-like O(1) inference scaling.
    """
    def __init__(self, d_model):
        super(RWKVLeo, self).__init__()
        self.d_model = d_model

        # Time mixing vectors
        self.time_decay = nn.Parameter(torch.ones(d_model))
        self.time_first = nn.Parameter(torch.ones(d_model))
        self.time_mix_k = nn.Parameter(torch.ones(1, 1, d_model))
        self.time_mix_v = nn.Parameter(torch.ones(1, 1, d_model))
        self.time_mix_r = nn.Parameter(torch.ones(1, 1, d_model))

        self.key = nn.Linear(d_model, d_model, bias=False)
        self.value = nn.Linear(d_model, d_model, bias=False)
        self.receptance = nn.Linear(d_model, d_model, bias=False)
        self.output = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, state=None):
        """
        x: (batch, seq_len, d_model)
        state: tuple of (last_x, num, den) representing O(1) hidden state
        """
        batch, seq_len, _ = x.shape
        
        if state is None:
            last_x = torch.zeros(batch, 1, self.d_model, device=x.device, dtype=x.dtype)
            num = torch.zeros(batch, 1, self.d_model, device=x.device, dtype=x.dtype)
            den = torch.zeros(batch, 1, self.d_model, device=x.device, dtype=x.dtype)
        else:
            last_x, num, den = state

        # Shift x by 1 in time
        xx = torch.cat([last_x, x[:, :-1, :]], dim=1)

        # Mix current and previous tokens
        xk = x * self.time_mix_k + xx * (1 - self.time_mix_k)
        xv = x * self.time_mix_v + xx * (1 - self.time_mix_v)
        xr = x * self.time_mix_r + xx * (1 - self.time_mix_r)

        k = self.key(xk)
        v = self.value(xv)
        r = torch.sigmoid(self.receptance(xr))

        # WKV calculation (simplified sequential for inference)
        # In a real batched training implementation, this is done via custom CUDA/C++ kernels.
        ys = []
        for i in range(seq_len):
            k_i = k[:, i:i+1, :]
            v_i = v[:, i:i+1, :]
            r_i = r[:, i:i+1, :]

            # Current output
            wkv = (num + torch.exp(self.time_first + k_i) * v_i) / \
                  (den + torch.exp(self.time_first + k_i))
            y_i = r_i * wkv
            ys.append(y_i)

            # Update state for next token
            num = torch.exp(-torch.exp(self.time_decay)) * num + torch.exp(k_i) * v_i
            den = torch.exp(-torch.exp(self.time_decay)) * den + torch.exp(k_i)
            
        y = torch.cat(ys, dim=1)
        out = self.output(y)

        # New state
        new_state = (x[:, -1:, :], num, den)
        
        return out, new_state
