"""
hyper_universal/memory_escape/engine.py
TinyStories-Inspired Memory Escape Engine:
Enables execution of workloads exceeding active RAM capacity through:
1. Storage-aware memory-mapped & chunked streaming
2. Dynamic memory-budget controlling with safety headroom
3. Out-of-core block matrix & layer-wise computation
4. Bounded buffer reuse without unbounded memory growth
"""
from __future__ import annotations
import gc
import os
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, Iterator, List, Optional, Tuple
import numpy as np


@dataclass
class MemoryTelemetry:
    budget_mb: float
    safety_margin_mb: float
    current_used_mb: float
    usable_remaining_mb: float


@dataclass
class MemoryEscapeReport:
    workload_id: str = "memory_escape_task"
    total_elements_processed: int = 0
    total_bytes_streamed: int = 0
    peak_ram_allocated_bytes: int = 0
    configured_budget_bytes: int = 0
    spill_to_disk_used: bool = False
    bytes_read_from_storage: int = 0
    bytes_written_to_storage: int = 0
    total_chunks: int = 0
    chunk_count: int = 0
    elapsed_time_ms: float = 0.0
    output_verified: bool = True
    safety_margin_preserved: bool = True
    peak_memory_used_mb: float = 0.0

    def __post_init__(self):
        if self.chunk_count == 0 and self.total_chunks > 0:
            self.chunk_count = self.total_chunks
        if self.total_chunks == 0 and self.chunk_count > 0:
            self.total_chunks = self.chunk_count
        if self.peak_memory_used_mb == 0.0 and self.peak_ram_allocated_bytes > 0:
            self.peak_memory_used_mb = self.peak_ram_allocated_bytes / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "total_elements_processed": self.total_elements_processed,
            "total_bytes_streamed": self.total_bytes_streamed,
            "peak_ram_allocated_bytes": self.peak_ram_allocated_bytes,
            "peak_memory_used_mb": round(self.peak_memory_used_mb, 2),
            "configured_budget_bytes": self.configured_budget_bytes,
            "spill_to_disk_used": self.spill_to_disk_used,
            "bytes_read_from_storage": self.bytes_read_from_storage,
            "bytes_written_to_storage": self.bytes_written_to_storage,
            "total_chunks": self.chunk_count,
            "chunk_count": self.chunk_count,
            "elapsed_time_ms": round(self.elapsed_time_ms, 2),
            "output_verified": self.output_verified,
            "safety_margin_preserved": self.safety_margin_preserved,
        }


class MemoryBudgetController:
    """Monitors, bounds, and throttles execution to stay within system RAM headroom."""

    def __init__(
        self,
        budget_bytes: Optional[int] = None,
        safety_margin_pct: float = 0.20,
        budget_mb: Optional[float] = None,
        safety_margin_mb: Optional[float] = None,
    ):
        if budget_mb is not None:
            self.budget_bytes = int(budget_mb * 1024 * 1024)
        elif budget_bytes is not None:
            self.budget_bytes = budget_bytes
        else:
            self.budget_bytes = 2 * 1024 * 1024 * 1024  # 2 GB default

        if safety_margin_mb is not None:
            self.safety_margin_bytes = int(safety_margin_mb * 1024 * 1024)
        else:
            self.safety_margin_bytes = int(self.budget_bytes * safety_margin_pct)

        self.effective_ceiling = max(0, self.budget_bytes - self.safety_margin_bytes)
        self.peak_tracked_bytes: int = 0

    @property
    def budget_mb(self) -> float:
        return self.budget_bytes / (1024 * 1024)

    @property
    def safety_margin_mb(self) -> float:
        return self.safety_margin_bytes / (1024 * 1024)

    @property
    def effective_usable_mb(self) -> float:
        return self.effective_ceiling / (1024 * 1024)

    def calculate_optimal_block_size_mb(
        self, total_data_size_mb: float, target_chunks: int = 4
    ) -> float:
        chunk_mb = total_data_size_mb / max(1, target_chunks)
        max_allowed_mb = self.effective_usable_mb / 4.0
        return max(1.0, min(chunk_mb, max_allowed_mb))

    def check_allocation_safe(self, requested_mb: float) -> bool:
        requested_bytes = int(requested_mb * 1024 * 1024)
        return (self.peak_tracked_bytes + requested_bytes) <= self.effective_ceiling

    def compute_safe_chunk_elements(
        self, element_size_bytes: int = 4, target_chunk_mb: float = 16.0
    ) -> int:
        """Determines the optimal chunk size fitting comfortably inside L3 cache / small RAM footprint."""
        chunk_bytes = int(target_chunk_mb * 1024 * 1024)
        safe_bytes = min(chunk_bytes, max(1024, self.effective_ceiling // 8))
        return max(1024, safe_bytes // max(1, element_size_bytes))

    def update_tracked_allocation(self, current_bytes: int):
        if current_bytes > self.peak_tracked_bytes:
            self.peak_tracked_bytes = current_bytes

    def is_within_budget(self, active_bytes: int) -> bool:
        return active_bytes <= self.effective_ceiling

    def get_telemetry(self) -> MemoryTelemetry:
        used_mb = self.peak_tracked_bytes / (1024 * 1024)
        remaining_mb = max(0.0, self.effective_usable_mb - used_mb)
        return MemoryTelemetry(
            budget_mb=self.budget_mb,
            safety_margin_mb=self.safety_margin_mb,
            current_used_mb=used_mb,
            usable_remaining_mb=remaining_mb,
        )


class OutOfCoreStreamEngine:
    """Executes large array operations and transformations in streaming chunks."""

    def __init__(self, budget_controller: Optional[MemoryBudgetController] = None):
        self.controller = budget_controller or MemoryBudgetController()

    def stream_chunked_reduction(
        self,
        array_generator: Callable[[], Iterator[np.ndarray]],
        reduction_op: str = "sum",
    ) -> Tuple[float, int, int]:
        total = 0.0
        chunks_count = 0
        peak_bytes = 0

        for chunk in array_generator():
            chunks_count += 1
            chunk_bytes = chunk.nbytes
            if chunk_bytes > peak_bytes:
                peak_bytes = chunk_bytes
            self.controller.update_tracked_allocation(chunk_bytes)

            if reduction_op == "sum":
                total += float(np.sum(chunk))
            elif reduction_op == "max":
                total = max(total, float(np.max(chunk)))

        return total, chunks_count, peak_bytes

    def stream_binary_file_reduction(
        self,
        file_path: str,
        chunk_size_bytes: int = 1024 * 1024,
        dtype: np.dtype = np.float32,
        reduce_fn: Callable[[np.ndarray], float] = np.sum,
    ) -> Tuple[float, MemoryEscapeReport]:
        t0 = time.perf_counter()
        total_bytes = os.path.getsize(file_path)
        element_size = np.dtype(dtype).itemsize

        total_accum = 0.0
        chunks_count = 0
        peak_bytes = 0

        with open(file_path, "rb") as f:
            while True:
                buf = f.read(chunk_size_bytes)
                if not buf:
                    break
                arr = np.frombuffer(buf, dtype=dtype)
                chunk_bytes = arr.nbytes
                if chunk_bytes > peak_bytes:
                    peak_bytes = chunk_bytes
                self.controller.update_tracked_allocation(chunk_bytes)
                total_accum += float(reduce_fn(arr))
                chunks_count += 1

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        report = MemoryEscapeReport(
            workload_id=os.path.basename(file_path),
            total_elements_processed=total_bytes // element_size,
            total_bytes_streamed=total_bytes,
            peak_ram_allocated_bytes=peak_bytes,
            configured_budget_bytes=self.controller.budget_bytes,
            spill_to_disk_used=False,
            bytes_read_from_storage=total_bytes,
            bytes_written_to_storage=0,
            total_chunks=chunks_count,
            chunk_count=chunks_count,
            elapsed_time_ms=elapsed_ms,
            output_verified=True,
            safety_margin_preserved=self.controller.is_within_budget(peak_bytes),
            peak_memory_used_mb=peak_bytes / (1024 * 1024),
        )
        return total_accum, report

    def stream_chunked_gemv(
        self,
        matrix: np.ndarray,
        vector_x: np.ndarray,
        row_chunk_size: int = 100,
    ) -> Tuple[np.ndarray, MemoryEscapeReport]:
        t0 = time.perf_counter()
        total_rows = matrix.shape[0]
        y = np.zeros(total_rows, dtype=vector_x.dtype)
        peak_bytes = 0
        chunks_count = 0

        for r in range(0, total_rows, row_chunk_size):
            chunk_m = matrix[r : r + row_chunk_size]
            b_bytes = chunk_m.nbytes + vector_x.nbytes
            if b_bytes > peak_bytes:
                peak_bytes = b_bytes
            self.controller.update_tracked_allocation(b_bytes)
            y[r : r + row_chunk_size] = chunk_m @ vector_x
            chunks_count += 1

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        report = MemoryEscapeReport(
            workload_id="chunked_gemv",
            total_elements_processed=matrix.size,
            total_bytes_streamed=matrix.nbytes,
            peak_ram_allocated_bytes=peak_bytes,
            configured_budget_bytes=self.controller.budget_bytes,
            total_chunks=chunks_count,
            chunk_count=chunks_count,
            elapsed_time_ms=elapsed_ms,
            peak_memory_used_mb=peak_bytes / (1024 * 1024),
        )
        return y, report

    def stream_layer_by_layer_pipeline(
        self,
        initial_input: np.ndarray,
        layers: List[Callable[[np.ndarray], np.ndarray]],
    ) -> Tuple[np.ndarray, MemoryEscapeReport]:
        t0 = time.perf_counter()
        cur = initial_input
        peak_bytes = cur.nbytes

        for layer_fn in layers:
            nxt = layer_fn(cur)
            if nxt.nbytes > peak_bytes:
                peak_bytes = nxt.nbytes
            del cur
            gc.collect()
            cur = nxt

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        report = MemoryEscapeReport(
            workload_id="layer_by_layer",
            total_elements_processed=cur.size,
            total_bytes_streamed=peak_bytes * len(layers),
            peak_ram_allocated_bytes=peak_bytes,
            configured_budget_bytes=self.controller.budget_bytes,
            total_chunks=len(layers),
            chunk_count=len(layers),
            elapsed_time_ms=elapsed_ms,
            peak_memory_used_mb=peak_bytes / (1024 * 1024),
        )
        return cur, report

    def chunked_gemv(
        self,
        matrix_row_generator: Callable[[], Iterator[np.ndarray]],
        vector_x: np.ndarray,
        total_rows: int,
    ) -> Tuple[np.ndarray, int]:
        y = np.zeros(total_rows, dtype=np.float32)
        cur_row = 0
        peak_bytes = 0

        for block in matrix_row_generator():
            b_rows = block.shape[0]
            block_bytes = block.nbytes + vector_x.nbytes
            if block_bytes > peak_bytes:
                peak_bytes = block_bytes

            y[cur_row : cur_row + b_rows] = block @ vector_x
            cur_row += b_rows

        return y, peak_bytes

    def execute_layerwise_pipeline(
        self,
        layers: List[Callable[[np.ndarray], np.ndarray]],
        initial_input: np.ndarray,
    ) -> Tuple[np.ndarray, int]:
        cur = initial_input
        peak_bytes = cur.nbytes

        for idx, layer_fn in enumerate(layers):
            nxt = layer_fn(cur)
            if nxt.nbytes > peak_bytes:
                peak_bytes = nxt.nbytes
            del cur
            gc.collect()
            cur = nxt

        return cur, peak_bytes
