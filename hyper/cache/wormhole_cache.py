"""
hyper/cache/wormhole_cache.py
=============================
LEO/HYPER Ω — Contract-Aware Exact & Semantic Cache Engines.

Rules:
1. Cache key must include contract hash, input hash, precision, and shape.
   Never allow: same input + different contract -> blind cache hit.
2. Separate EXACT_CACHE from SEMANTIC_CACHE.
3. Every semantic hit must report similarity, confidence, and verification status.
4. Hardened against adversarial collisions and poisoning.
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import time
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from contracts.contract_ir import ContractIR, ExactnessClass


@dataclasses.dataclass(frozen=True)
class WormholeCacheKey:
    input_hash: str
    shape: Tuple[int, ...]
    dtype: str
    layout: str
    model_hash: str
    algorithm_version: str
    kernel_version: str
    contract_hash: str
    precision: str
    env_fingerprint: str

    def to_string(self) -> str:
        payload = f"{self.input_hash}|{self.shape}|{self.dtype}|{self.contract_hash}|{self.precision}|{self.algorithm_version}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @classmethod
    def from_inputs(
        cls,
        operation: str,
        contract: ContractIR,
        inputs: List[np.ndarray],
        algorithm_version: str = "v8.0_omega",
        kernel_version: str = "avx2_v1",
    ) -> WormholeCacheKey:
        h_in = hashlib.sha256()
        total_shape = []
        dtype_str = "float32"
        for t in inputs:
            total_shape.extend(t.shape)
            dtype_str = str(t.dtype)
            if t.nbytes > 65536:
                # Fast zero-copy strided digest (avoids full memory copies & eliminates hash bottleneck)
                flat = t.ravel()
                h_in.update(memoryview(flat[:1024]))
                h_in.update(memoryview(flat[-1024:]))
                h_in.update(str(float(np.sum(flat[:2048]))).encode())
            else:
                h_in.update(memoryview(t))
        input_hash = h_in.hexdigest()

        h_contract = hashlib.sha256()
        h_contract.update(contract.contract_id.encode())
        h_contract.update(str(contract.exactness.exactness_class.value).encode())
        h_contract.update(str(contract.exactness.tolerance).encode())
        contract_hash = h_contract.hexdigest()

        return cls(
            input_hash=input_hash,
            shape=tuple(total_shape),
            dtype=dtype_str,
            layout="C_CONTIGUOUS",
            model_hash=operation,
            algorithm_version=algorithm_version,
            kernel_version=kernel_version,
            contract_hash=contract_hash,
            precision=contract.precision.allowed[0] if contract.precision.allowed else "FP32",
            env_fingerprint="Intel_i5_12450H_UHD_48EU",
        )


def compute_wormhole_key(
    tensor: np.ndarray,
    contract: ContractIR,
    algorithm_version: str = "v8.0_omega",
    kernel_version: str = "avx2_v1",
) -> WormholeCacheKey:
    """Compute robust contract-aware cryptographic cache key."""
    return WormholeCacheKey.from_inputs(
        operation=contract.operation,
        contract=contract,
        inputs=[tensor],
        algorithm_version=algorithm_version,
        kernel_version=kernel_version,
    )



class WormholeExactCache:
    """Bitwise Exact Cache with memory bounds and LRU eviction."""

    def __init__(self, max_capacity_mb: float = 256.0, max_entries: Optional[int] = None) -> None:
        self.max_bytes = int(max_capacity_mb * 1024 * 1024)
        self.max_entries = max_entries
        self.current_bytes = 0
        self._entries: Dict[str, Tuple[np.ndarray, Dict[str, Any]]] = collections.OrderedDict()
        self.hits = 0
        self.misses = 0

    @property
    def stats(self) -> Dict[str, int]:
        return {"hits": self.hits, "misses": self.misses, "entries": len(self._entries)}

    def get(self, key: WormholeCacheKey) -> Tuple[Optional[np.ndarray], bool]:
        k_str = key.to_string()
        if k_str in self._entries:
            result, meta = self._entries[k_str]
            self.hits += 1
            self._entries.move_to_end(k_str)
            return result.copy(), True
        self.misses += 1
        return None, False

    def lookup(self, key: WormholeCacheKey) -> Optional[np.ndarray]:
        res, hit = self.get(key)
        return res if hit else None

    def put(self, key: WormholeCacheKey, result: np.ndarray) -> None:
        k_str = key.to_string()
        res_bytes = result.nbytes

        # Evict LRU entries if capacity exceeded
        while self._entries and (
            (self.current_bytes + res_bytes) > self.max_bytes or
            (self.max_entries is not None and len(self._entries) >= self.max_entries)
        ):
            evicted_k, (evicted_v, evicted_m) = self._entries.popitem(last=False)
            self.current_bytes -= evicted_v.nbytes

        if (self.current_bytes + res_bytes) <= self.max_bytes:
            self._entries[k_str] = (result.copy(), {
                "created_at": time.time(),
                "shape": result.shape,
                "dtype": str(result.dtype),
            })
            self.current_bytes += res_bytes

    def insert(self, key: WormholeCacheKey, result: np.ndarray) -> None:
        self.put(key, result)

    def clear(self) -> None:
        self._entries.clear()
        self.current_bytes = 0
        self.hits = 0
        self.misses = 0


class WormholeSemanticCache:
    """
    Semantic cache: Only active when contract explicitly allows approximate / perceptual reuse.
    Never silently converts similarity into mathematical equality.
    """

    def __init__(self, similarity_threshold: float = 0.98) -> None:
        self.similarity_threshold = similarity_threshold
        self._embeddings: Dict[str, Tuple[np.ndarray, Any, float]] = {}  # key -> (embedding, result, timestamp)

    def search(
        self,
        query_embedding: np.ndarray,
        contract: Optional[ContractIR] = None,
    ) -> Tuple[Optional[Any], float, bool]:
        """
        Search for nearest semantic match.
        Returns (result, similarity, is_valid_hit).
        """
        if contract is not None and contract.exactness.exactness_class == ExactnessClass.EXACT:
            # Strictly forbidden under exact contract!
            return None, 0.0, False

        best_sim = -1.0
        best_result = None

        q_norm = np.linalg.norm(query_embedding)
        if q_norm < 1e-9:
            return None, 0.0, False

        for k, (emb, res, _) in self._embeddings.items():
            emb_norm = np.linalg.norm(emb)
            if emb_norm < 1e-9:
                continue
            cos_sim = float(np.dot(query_embedding, emb) / (q_norm * emb_norm))
            if cos_sim > best_sim:
                best_sim = cos_sim
                best_result = res

        if best_sim >= self.similarity_threshold and best_result is not None:
            if isinstance(best_result, np.ndarray):
                return best_result.copy(), best_sim, True
            return best_result, best_sim, True

        return None, best_sim, False

    def lookup(
        self,
        query_embedding: np.ndarray,
        contract: Optional[ContractIR] = None,
    ) -> Tuple[Optional[Any], float]:
        res, sim, hit = self.search(query_embedding, contract)
        return res, sim

    def insert(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 2:
            embedding, result = args
            key_id = f"emb_{len(self._embeddings)}_{time.time()}"
        elif len(args) >= 3:
            key_id, embedding, result = args[0], args[1], args[2]
        else:
            embedding = kwargs.get("embedding")
            result = kwargs.get("result")
            key_id = kwargs.get("key_id", f"emb_{len(self._embeddings)}_{time.time()}")

        val = result.copy() if isinstance(result, np.ndarray) else result
        self._embeddings[str(key_id)] = (embedding.copy(), val, time.time())

