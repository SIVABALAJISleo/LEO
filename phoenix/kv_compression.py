"""
phoenix/kv_compression.py
KV Cache Compression Engines:
  1. StreamingKV — evicts oldest tokens, keeps recent + important (H2O)
  2. H2O Heavy-Hitter Oracle — keeps only the most attended-to tokens
  3. SnapKV — compresses KV cache by clustering similar key-value pairs
"""

import torch
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class StreamingKVCache:
    """
    Sliding-window KV cache with heavy-hitter retention.
    Keeps:
      - `sink_size` initial tokens always (attention sink phenomenon)
      - `window_size` most recent tokens
      - Top `top_k_heavy` tokens by cumulative attention score
    """

    def __init__(self, sink_size: int = 4, window_size: int = 256,
                 top_k_heavy: int = 64):
        self.sink_size    = sink_size
        self.window_size  = window_size
        self.top_k_heavy  = top_k_heavy

        self.keys:    Optional[torch.Tensor] = None   # (seq, heads, dim)
        self.values:  Optional[torch.Tensor] = None
        self.attn_scores: Optional[torch.Tensor] = None  # (seq,) cumulative

    def update(self, new_key: torch.Tensor, new_val: torch.Tensor,
               attn_weight: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Append new K/V, update attention accumulator, compress if over budget.
        new_key/val: (1, heads, dim)
        Returns: current K/V cache tensors
        """
        if self.keys is None:
            self.keys  = new_key
            self.values = new_val
            self.attn_scores = torch.zeros(1)
        else:
            self.keys   = torch.cat([self.keys,  new_key],  dim=0)
            self.values = torch.cat([self.values, new_val], dim=0)
            new_score   = attn_weight.mean() if attn_weight is not None else torch.tensor(0.0)
            self.attn_scores = torch.cat([self.attn_scores, new_score.unsqueeze(0)])

        total_budget = self.sink_size + self.window_size + self.top_k_heavy
        seq_len = self.keys.size(0)

        if seq_len > total_budget:
            self._compress()

        return self.keys, self.values

    def _compress(self):
        """Evict tokens: keep sinks + window + heavy-hitters."""
        seq_len = self.keys.size(0)
        sink_end = self.sink_size

        # Candidate non-sink, non-recent tokens
        middle_start = sink_end
        middle_end   = max(sink_end, seq_len - self.window_size)
        recent_start = middle_end

        if middle_start < middle_end:
            middle_scores = self.attn_scores[middle_start:middle_end]
            k = min(self.top_k_heavy, middle_end - middle_start)
            _, heavy_rel_idx = torch.topk(middle_scores, k)
            heavy_abs_idx    = heavy_rel_idx + middle_start
            heavy_abs_idx, _ = heavy_abs_idx.sort()

            sink_idx   = torch.arange(sink_end)
            recent_idx = torch.arange(recent_start, seq_len)
            keep_idx   = torch.cat([sink_idx, heavy_abs_idx, recent_idx]).unique()

            self.keys        = self.keys[keep_idx]
            self.values      = self.values[keep_idx]
            self.attn_scores = self.attn_scores[keep_idx]

            evicted = seq_len - self.keys.size(0)
            if evicted > 0:
                logger.debug(f"[StreamingKV] Evicted {evicted} tokens. "
                             f"Cache: {self.keys.size(0)} tokens.")


class SnapKVCompressor:
    """
    SnapKV-style key-value compression via cluster-based deduplication.
    Finds groups of nearly-identical key vectors and replaces them with
    their centroid, compressing the cache by up to 5x.
    """

    def __init__(self, similarity_threshold: float = 0.98):
        self.threshold = similarity_threshold

    def compress(self, keys: torch.Tensor, values: torch.Tensor,
                 max_clusters: int = 64) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        keys:   (seq, heads, dim) — compresses over seq dimension.
        Returns compressed (seq', heads, dim) for both K and V.
        """
        seq_len, heads, dim = keys.shape
        if seq_len <= max_clusters:
            return keys, values

        # Flatten for similarity: (seq, heads*dim)
        k_flat = keys.reshape(seq_len, -1).float()
        k_norm = k_flat / (k_flat.norm(dim=1, keepdim=True) + 1e-8)

        # Greedy clustering: assign each token to nearest existing centroid
        centroids   = [k_norm[0]]
        assignments = [0]
        centroid_keys   = [keys[0]]
        centroid_values = [values[0]]

        for i in range(1, seq_len):
            sims = torch.stack([(k_norm[i] * c).sum() for c in centroids])
            best_sim, best_c = sims.max(0)

            if best_sim.item() >= self.threshold and len(centroids) >= max_clusters:
                # Merge: running average of centroid K and V
                assignments.append(int(best_c))
                # Update centroid (running mean)
                n = sum(1 for a in assignments if a == int(best_c))
                centroid_keys[int(best_c)]   = (centroid_keys[int(best_c)] * (n-1) + keys[i]) / n
                centroid_values[int(best_c)] = (centroid_values[int(best_c)] * (n-1) + values[i]) / n
            else:
                # New cluster
                if len(centroids) < max_clusters:
                    centroids.append(k_norm[i])
                    centroid_keys.append(keys[i])
                    centroid_values.append(values[i])
                    assignments.append(len(centroids) - 1)
                else:
                    assignments.append(int(best_c))

        compressed_k = torch.stack(centroid_keys)   # (clusters, heads, dim)
        compressed_v = torch.stack(centroid_values)
        logger.debug(f"[SnapKV] Compressed {seq_len} → {compressed_k.size(0)} tokens "
                     f"({compressed_k.size(0)/seq_len*100:.1f}% retained).")
        return compressed_k, compressed_v


class KiviZipCacheCompressor:
    """
    KIVI & ZipCache Asymmetric 2-bit Key/Value Cache Quantizer.
    Reduces memory footprints by 4x for massive context windows (up to 256K).
    """
    def __init__(self, group_size: int = 32):
        self.group_size = group_size

    def quantize_asymmetric_2bit(self, tensor: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Quantizes key or value tensors to 2-bit representation asymmetric values.
        Returns: (quantized_2bit_packed, scale, zero_point)
        """
        # Determine group min/max dimensions
        shape = tensor.shape
        # Quantize along token sequence dimension
        flat_tensor = tensor.reshape(-1, self.group_size)
        
        t_min = flat_tensor.min(dim=-1, keepdim=True)[0]
        t_max = flat_tensor.max(dim=-1, keepdim=True)[0]
        
        # 2-bit quantization level scale: 2^2 - 1 = 3 levels
        scale = (t_max - t_min) / 3.0
        scale = torch.clamp(scale, min=1e-5)
        
        zero_point = torch.round(-t_min / scale)
        
        # Map values to [0, 3] integers
        quantized = torch.clamp(torch.round(flat_tensor / scale + zero_point), 0, 3).to(torch.uint8)
        
        # Pack 4 2-bit values into a single uint8 byte
        packed_shape = (quantized.shape[0], quantized.shape[1] // 4)
        packed = torch.zeros(packed_shape, dtype=torch.uint8)
        for i in range(4):
            packed |= (quantized[:, i::4] & 0x03) << (2 * i)
            
        return packed, scale, zero_point



    def dequantize_asymmetric_2bit(self, packed: torch.Tensor, scale: torch.Tensor, zero_point: torch.Tensor, original_shape: Tuple) -> torch.Tensor:
        """
        Dequantizes 2-bit packed representation back to full tensors.
        """
        num_tokens, packed_dim = packed.shape
        quantized = torch.zeros((num_tokens, packed_dim * 4), dtype=torch.uint8, device=packed.device)
        
        for i in range(4):
            quantized[:, i::4] = (packed >> (2 * i)) & 0x03
            
        flat_tensor = (quantized.to(torch.float32) - zero_point) * scale
        return flat_tensor.reshape(original_shape)
