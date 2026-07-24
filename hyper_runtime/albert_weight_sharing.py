"""
albert_weight_sharing.py
S3: ALBERT Cross-Layer Sharing + S6: Weight Tying

Reduces memory footprint radically:
1. Weight Tying: The embedding matrix is reused as the final projection matrix.
2. Cross-Layer Sharing: Instead of N unique transformer blocks, we define a small 
   set of blocks (e.g. 4) and loop them multiple times to achieve the depth of N layers.
"""

import torch
import torch.nn as nn

class TransformerBlock(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.ffn = nn.Linear(hidden_size, hidden_size)
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        # Assuming external attention mechanism is passed in or integrated

    def forward(self, x, attn_fn):
        res = x
        x = self.norm1(x)
        x, _ = attn_fn(x)
        x = x + res
        
        res = x
        x = self.norm2(x)
        x = torch.relu(self.ffn(x))
        return x + res

class SharedWeightsModel(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_unique_layers, total_layers):
        super().__init__()
        self.hidden_size = hidden_size
        self.total_layers = total_layers
        self.num_unique_layers = num_unique_layers
        
        # S6: Weight Tying (Embedding == Unembedding)
        self.embeddings = nn.Embedding(vocab_size, hidden_size)
        
        # S3: Cross-Layer Sharing
        # We only instantiate `num_unique_layers` (e.g., 4) instead of `total_layers` (e.g., 32)
        self.shared_blocks = nn.ModuleList([
            TransformerBlock(hidden_size) for _ in range(num_unique_layers)
        ])
        
    def get_unembedding(self, x):
        """Reuses embedding weights for the final logits projection."""
        # x shape: [B, seq, H]
        # emb weight shape: [V, H]
        # output shape: [B, seq, V]
        return torch.matmul(x, self.embeddings.weight.t())

    def forward(self, input_ids, attention_mechanisms):
        x = self.embeddings(input_ids)
        
        # Route through the shared blocks recursively
        for i in range(self.total_layers):
            block_idx = i % self.num_unique_layers
            block = self.shared_blocks[block_idx]
            attn = attention_mechanisms[block_idx]
            
            x = block(x, attn)
            
        # Unembed using tied weights
        logits = self.get_unembedding(x)
        return logits
