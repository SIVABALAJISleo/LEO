import numpy as np
import warnings
from hyper_runtime.cpu_orchestrator.cache_aware_tiling import CacheAwareTiler
from core_ai.architectures.kan_subsumption import KANSubsumptionEngine
from core_ai.architectures.topological_shape import TopologicalShapePreserver

# Attempt to load the C++ DFA engine, fallback to simulated logic if compiler failed
try:
    import dfa_engine_cpp
    HAS_DFA = True
except ImportError:
    HAS_DFA = False
    warnings.warn("DFA Engine C++ extension not found. Using simulated fallback.")

class AlgorithmicAlchemyContract:
    """
    The main routing wrapper that intercepts compute requests and routes them
    to the optimal B300-bypass engine based on precision requirements.
    """
    def __init__(self):
        self.tiler = CacheAwareTiler(l2_cache_size_kb=1280)
        self.kan_engine = KANSubsumptionEngine()
        
    def execute_gemm(self, A: np.ndarray, B: np.ndarray, precision_req: str = 'INT8', preserve_shape: bool = False) -> np.ndarray:
        """
        Executes a Matrix Multiplication by bypassing standard FLOPS based on the contract.
        
        Args:
            A: Input activation matrix
            B: Weight matrix
            precision_req: 'INT8', 'FP32', or 'KAN_APPROX'
            preserve_shape: If True, uses Virtual Padding for Tensor-Train shapes.
        """
        M, K = A.shape
        _, N = B.shape
        
        # 1. Shape Preservation Bypass
        if preserve_shape and M == 256 and N == 256:
            preserver = TopologicalShapePreserver(original_shape=(256, 256), compressed_shape=(128, 128))
            return preserver.einsum_contraction(A, B)
            
        # 2. KAN Subsumption Bypass (Functional Approximation)
        if precision_req == 'KAN_APPROX':
            return self.kan_engine.execute(A, B)
            
        # 3. DFA Engine Bypass (Int8 / Int4)
        if precision_req == 'INT8':
            if A.dtype != np.int8:
                A = np.clip(A, -128, 127).astype(np.int8)
            if B.dtype != np.int8:
                B = np.clip(B, -128, 127).astype(np.int8)
                
            if HAS_DFA:
                # Use C++ Trie-Lookup
                # L1 micro-tiling applied under the hood
                C, _ = self.tiler.tile_matrix_multiply(A, B, compute_func=dfa_engine_cpp.dfa_gemm_int8)
                return C
            else:
                # Simulated DFA fallback
                C, _ = self.tiler.tile_matrix_multiply(A, B, compute_func=lambda a, b: np.dot(a.astype(np.int32), b.astype(np.int32)))
                return C
                
        # 4. FP32 Fallback (Cache-Aware Tiling)
        C, telemetry = self.tiler.tile_matrix_multiply(A, B, compute_func=np.dot)
        return C
