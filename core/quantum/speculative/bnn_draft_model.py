"""
Binary Neural Network Draft Model for Speculative Decoding
Uses 1.58-bit quantization for ultra-fast token generation
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple
import math

class BinaryLinear(nn.Module):
    """Binary linear layer with 1.58-bit weights"""
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Initialize weights as ternary {-1, 0, 1}
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter('bias', None)
            
    def quantize_weights(self) -> torch.Tensor:
        """Quantize weights to 1.58-bit (ternary)"""
        # Compute threshold
        threshold = 0.7 * self.weight.abs().mean()
        
        # Quantize to ternary {-1, 0, 1}
        quantized = torch.where(
            self.weight > threshold,
            torch.ones_like(self.weight),
            torch.where(
                self.weight < -threshold,
                -torch.ones_like(self.weight),
                torch.zeros_like(self.weight)
            )
        )
        return quantized
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Quantize weights during forward pass
        binary_weight = self.quantize_weights()
        
        # Standard computation fallback or optimized custom simulation
        if x.dtype == torch.float32 or x.dtype == torch.float16:
            return F.linear(x, binary_weight, self.bias)
        else:
            # Cast input to float for compatibility with PyTorch standard linear ops
            x_float = x.to(torch.float32)
            out = F.linear(x_float, binary_weight, self.bias)
            return out


class BinaryAttention(nn.Module):
    """Binary attention mechanism with scalable dimension projection"""
    
    def __init__(self, embed_dim: int, num_heads: int):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        self.q_proj = BinaryLinear(embed_dim, embed_dim)
        self.k_proj = BinaryLinear(embed_dim, embed_dim)
        self.v_proj = BinaryLinear(embed_dim, embed_dim)
        self.out_proj = BinaryLinear(embed_dim, embed_dim)
        
    def forward(
        self, 
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        # Project to Q, K, V
        Q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attn_weights = F.softmax(scores, dim=-1)
        attn_output = torch.matmul(attn_weights, V)
        
        # Reshape and project output
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_dim)
        return self.out_proj(attn_output)


class BNNDraftModel(nn.Module):
    """
    Binary Neural Network Draft Model for speculative decoding
    Generates candidate tokens quickly using 1.58-bit quantization
    """
    
    def __init__(self, vocab_size: int, embed_dim: int = 256, num_layers: int = 4):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        
        # Embedding layer (kept in full precision)
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Binary transformer layers
        self.layers = nn.ModuleList([
            nn.ModuleDict({
                'attention': BinaryAttention(embed_dim, num_heads=8),
                'norm1': nn.LayerNorm(embed_dim),
                'ffn': nn.Sequential(
                    BinaryLinear(embed_dim, embed_dim * 4),
                    nn.ReLU(),
                    BinaryLinear(embed_dim * 4, embed_dim)
                ),
                'norm2': nn.LayerNorm(embed_dim)
            }) for _ in range(num_layers)
        ])
        
        # Output projection (kept in full precision)
        self.output_proj = nn.Linear(embed_dim, vocab_size)
        
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        # Embed tokens
        x = self.embedding(input_ids)
        
        # Apply binary transformer layers
        for layer in self.layers:
            # Self-attention
            attn_output = layer['attention'](x)
            x = layer['norm1'](x + attn_output)
            
            # Feed-forward
            ffn_output = layer['ffn'](x)
            x = layer['norm2'](x + ffn_output)
        
        # Project to vocabulary
        logits = self.output_proj(x)
        return logits
    
    def generate_draft_tokens(
        self,
        input_ids: torch.Tensor,
        num_draft_tokens: int = 5,
        temperature: float = 0.8
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate draft tokens for speculative decoding
        
        Returns:
            draft_tokens: Generated token IDs (batch, num_draft_tokens)
            draft_logits: Logits for each draft token (batch, num_draft_tokens, vocab_size)
        """
        draft_tokens = []
        draft_logits = []
        
        current_input = input_ids.clone()
        
        for _ in range(num_draft_tokens):
            # Get logits for next token
            logits = self.forward(current_input)
            next_token_logits = logits[:, -1, :] / max(temperature, 1e-5)
            
            # Sample token
            probs = F.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            draft_tokens.append(next_token)
            draft_logits.append(next_token_logits)
            
            # Append to input for next iteration
            current_input = torch.cat([current_input, next_token], dim=-1)
        
        # Stack results
        # draft_tokens: list of shape [batch, 1] -> stack to [batch, num_draft_tokens]
        # draft_logits: list of shape [batch, vocab_size] -> stack to [batch, num_draft_tokens, vocab_size]
        draft_tokens_tensor = torch.cat(draft_tokens, dim=-1)
        draft_logits_tensor = torch.stack(draft_logits, dim=1)
        
        return draft_tokens_tensor, draft_logits_tensor
