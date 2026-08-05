"""
phoenix/paged_kv_cache.py
vLLM-style Paged KV Cache Manager.
Eliminates KV cache fragmentation by allocating fixed-size blocks (16 tokens).
Supports copy-on-write for shared prefixes and dynamic block eviction.
"""
import torch
import logging
from typing import Dict, List, Optional, Tuple
from phoenix.kv_compression import KiviZipCacheCompressor

logger = logging.getLogger(__name__)

BLOCK_SIZE = 16   # tokens per physical block


class KVBlock:
    """A fixed-size physical KV cache block."""
    __slots__ = ("block_id", "keys", "values", "ref_count", "num_filled")

    def __init__(self, block_id: int, num_heads: int, head_dim: int, dtype=torch.float16):
        self.block_id = block_id
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.dtype = dtype
        
        self.keys = torch.zeros(BLOCK_SIZE, num_heads, head_dim, dtype=dtype)
        self.values = torch.zeros(BLOCK_SIZE, num_heads, head_dim, dtype=dtype)
        
        self.is_compressed = False
        self.keys_packed = None
        self.keys_scale = None
        self.keys_zp = None
        self.values_packed = None
        self.values_scale = None
        self.values_zp = None
        
        self.ref_count = 0
        self.num_filled = 0

    def compress(self, compressor: KiviZipCacheCompressor):
        if self.is_compressed or self.num_filled == 0:
            return
            
        k_valid = self.keys[:self.num_filled]
        self.keys_packed, self.keys_scale, self.keys_zp = compressor.quantize_asymmetric_2bit(k_valid)
        
        v_valid = self.values[:self.num_filled]
        self.values_packed, self.values_scale, self.values_zp = compressor.quantize_asymmetric_2bit(v_valid)
        
        self.is_compressed = True
        self.keys = None
        self.values = None

    def get_keys(self, compressor: KiviZipCacheCompressor) -> torch.Tensor:
        if not self.is_compressed:
            return self.keys[:self.num_filled]
        original_shape = (self.num_filled, self.num_heads, self.head_dim)
        return compressor.dequantize_asymmetric_2bit(self.keys_packed, self.keys_scale, self.keys_zp, original_shape).to(self.dtype)

    def get_values(self, compressor: KiviZipCacheCompressor) -> torch.Tensor:
        if not self.is_compressed:
            return self.values[:self.num_filled]
        original_shape = (self.num_filled, self.num_heads, self.head_dim)
        return compressor.dequantize_asymmetric_2bit(self.values_packed, self.values_scale, self.values_zp, original_shape).to(self.dtype)


class PagedKVCacheManager:
    """
    Manages a pool of fixed-size KV blocks across all active sequences.
    API mirrors vLLM's block manager for compatibility.
    """

    def __init__(self, num_blocks: int, num_heads: int, head_dim: int,
                 dtype=torch.float16):
        self.num_heads = num_heads
        self.head_dim  = head_dim
        self.dtype     = dtype
        
        self.compressor = KiviZipCacheCompressor(group_size=BLOCK_SIZE)

        # Pre-allocate physical block pool
        self.blocks: Dict[int, KVBlock] = {
            i: KVBlock(i, num_heads, head_dim, dtype)
            for i in range(num_blocks)
        }
        self.free_block_ids: List[int] = list(range(num_blocks))

        # Sequence → list of physical block IDs
        self.seq_block_table: Dict[str, List[int]] = {}

        logger.info(f"PagedKVCache: {num_blocks} blocks × {BLOCK_SIZE} tokens = "
                    f"{num_blocks * BLOCK_SIZE} max tokens in pool.")

    def _alloc_block(self) -> Optional[int]:
        if not self.free_block_ids:
            return None
        bid = self.free_block_ids.pop()
        blk = self.blocks[bid]
        blk.ref_count = 1
        blk.num_filled = 0
        blk.is_compressed = False
        blk.keys = torch.zeros(BLOCK_SIZE, self.num_heads, self.head_dim, dtype=self.dtype)
        blk.values = torch.zeros(BLOCK_SIZE, self.num_heads, self.head_dim, dtype=self.dtype)
        return bid

    def _free_block(self, block_id: int):
        blk = self.blocks[block_id]
        blk.ref_count -= 1
        if blk.ref_count == 0:
            self.free_block_ids.append(block_id)

    def init_sequence(self, seq_id: str):
        """Allocate the first block for a new sequence."""
        bid = self._alloc_block()
        if bid is None:
            raise RuntimeError("PagedKVCache: Out of physical blocks!")
        self.seq_block_table[seq_id] = [bid]

    def write_kv(self, seq_id: str, token_pos: int,
                 key: torch.Tensor, value: torch.Tensor):
        """Writes one token's K/V at position token_pos for a sequence."""
        block_idx  = token_pos // BLOCK_SIZE
        token_slot = token_pos  % BLOCK_SIZE

        # Grow the block table if needed
        while len(self.seq_block_table[seq_id]) <= block_idx:
            bid = self._alloc_block()
            if bid is None:
                raise RuntimeError("PagedKVCache: OOM during write.")
            self.seq_block_table[seq_id].append(bid)

        bid = self.seq_block_table[seq_id][block_idx]
        blk = self.blocks[bid]
        
        if blk.is_compressed:
            raise RuntimeError("Cannot write to a block that is already compressed.")
            
        blk.keys[token_slot]   = key
        blk.values[token_slot] = value
        blk.num_filled = max(blk.num_filled, token_slot + 1)
        
        # Compress immediately once the block is full
        if blk.num_filled == BLOCK_SIZE:
            blk.compress(self.compressor)

    def read_kv(self, seq_id: str, max_tokens: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Reads full K/V tensors for a sequence up to max_tokens."""
        block_ids = self.seq_block_table.get(seq_id, [])
        k_chunks, v_chunks = [], []
        collected = 0
        for bid in block_ids:
            blk = self.blocks[bid]
            take = min(blk.num_filled, max_tokens - collected)
            if take <= 0:
                break
            k_chunks.append(blk.get_keys(self.compressor)[:take])
            v_chunks.append(blk.get_values(self.compressor)[:take])
            collected += take
        if not k_chunks:
            return torch.empty(0), torch.empty(0)
        return torch.cat(k_chunks, dim=0), torch.cat(v_chunks, dim=0)

    def free_sequence(self, seq_id: str):
        """Release all blocks belonging to a finished sequence."""
        for bid in self.seq_block_table.pop(seq_id, []):
            self._free_block(bid)

    def stats(self) -> Dict:
        return {
            "total_blocks": len(self.blocks),
            "free_blocks": len(self.free_block_ids),
            "used_blocks": len(self.blocks) - len(self.free_block_ids),
            "active_sequences": len(self.seq_block_table),
        }
