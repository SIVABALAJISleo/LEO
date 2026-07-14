import torch
import torch.nn as nn
import torch.nn.functional as F

class MambaLeo(nn.Module):
    """
    O(1) State Space Model (SSM) block replacing standard Transformer Attention.
    Eliminates the expanding KV cache by maintaining a fixed-size recurrent hidden state.
    """
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        super(MambaLeo, self).__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(self.expand * self.d_model)

        # Projections
        self.in_proj = nn.Linear(self.d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            bias=True,
            kernel_size=d_conv,
            groups=self.d_inner,
            padding=d_conv - 1,
        )
        
        # SSM parameters
        self.x_proj = nn.Linear(self.d_inner, self.d_state * 2 + 1, bias=False)
        self.dt_proj = nn.Linear(1, self.d_inner, bias=True)
        
        # S4D State representation
        A = torch.arange(1, self.d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=False)

    def forward(self, x, hidden_state=None):
        """
        x: (batch, seq_len, d_model)
        hidden_state: (batch, d_inner, d_state) or None. Represents the O(1) context.
        """
        batch, seq_len, _ = x.shape

        # 1. Input Projection
        x_and_res = self.in_proj(x) # (B, L, 2 * d_inner)
        x, res = x_and_res.split(split_size=self.d_inner, dim=-1)

        # 2. 1D Convolution
        x = x.transpose(1, 2) # (B, d_inner, L)
        x = self.conv1d(x)[:, :, :seq_len] # Truncate padding
        x = x.transpose(1, 2) # (B, L, d_inner)
        x = F.silu(x)

        # 3. SSM State Updates (Parallel Scan for training, sequential for inference)
        # We will simulate the recurrent scan for inference here to prove O(1) state.
        
        ssm_params = self.x_proj(x) # (B, L, 2*d_state + 1)
        delta, B, C = torch.split(ssm_params, [1, self.d_state, self.d_state], dim=-1)
        
        delta = F.softplus(self.dt_proj(delta)) # (B, L, d_inner)
        A = -torch.exp(self.A_log.float()) # (d_inner, d_state)

        # O(1) Inference recurrence loop
        if hidden_state is None:
            hidden_state = torch.zeros(batch, self.d_inner, self.d_state, device=x.device, dtype=x.dtype)
            
        ys = []
        for i in range(seq_len):
            x_i = x[:, i, :] # (B, d_inner)
            dt_i = delta[:, i, :] # (B, d_inner)
            B_i = B[:, i, :] # (B, d_state)
            C_i = C[:, i, :] # (B, d_state)

            # Discretize (Zero-order hold)
            # dA = exp(dt * A)
            dA_i = torch.exp(dt_i.unsqueeze(-1) * A) # (B, d_inner, d_state)
            # dB = (exp(dt * A) - I) / A * B  (Simplified)
            dB_i = (dA_i - 1.0) / A * B_i.unsqueeze(1) # (B, d_inner, d_state)

            # State Update: h_t = dA * h_{t-1} + dB * x_t
            hidden_state = dA_i * hidden_state + dB_i * x_i.unsqueeze(-1)
            
            # Output: y_t = C * h_t + D * x_t
            y_i = (hidden_state * C_i.unsqueeze(1)).sum(dim=-1) + self.D * x_i
            ys.append(y_i)
            
        y = torch.stack(ys, dim=1) # (B, L, d_inner)
        
        # 4. Gating and Output
        y = y * F.silu(res)
        out = self.out_proj(y)

        # Note: In standard generation, we'd return (out, hidden_state) to persist context
        # without growing memory. For PyTorch drop-in compatibility, we just return out.
        return out, hidden_state
