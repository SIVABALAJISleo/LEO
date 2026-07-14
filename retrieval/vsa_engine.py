import numpy as np
import logging

logger = logging.getLogger(__name__)

class VectorSymbolicArchitecture:
    """
    Vector Symbolic Architecture (VSA) / Hyperdimensional Computing Engine.
    Represents concepts as 10,000-dimensional binary vectors.
    Reasoning executes strictly via bitwise XOR and POPCNT.
    """
    def __init__(self, dim: int = 10000):
        self.dim = dim
        self.memory = {}
        # We pack 10,000 bits into an array of uint64 for ultra-fast bitwise operations.
        self.num_uint64 = (dim + 63) // 64

    def _generate_random_vector(self) -> np.ndarray:
        """Generates a random 10,000-D hypervector (packed into uint64)."""
        # Each random integer gives 64 bits.
        return np.random.randint(0, 2**64, size=self.num_uint64, dtype=np.uint64)

    def bind(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """
        Binds two concepts together (e.g., Role: 'Capital' + Entity: 'France').
        In binary VSA, binding is bitwise XOR.
        """
        return np.bitwise_xor(v1, v2)

    def bundle(self, vectors: list[np.ndarray]) -> np.ndarray:
        """
        Bundles multiple concepts into a single superposition (Set union).
        In binary VSA, bundling is majority voting (thresholded sum).
        Since we use packed uint64, we unpack, sum, and threshold, then repack.
        """
        if not vectors:
            return np.zeros(self.num_uint64, dtype=np.uint64)
            
        unpacked = np.array([np.unpackbits(v.view(np.uint8)) for v in vectors])
        # Sum across the bundle
        majority = np.sum(unpacked, axis=0) > (len(vectors) / 2.0)
        # Repack to uint64
        return np.packbits(majority).view(np.uint64)

    def shift(self, v: np.ndarray, places: int = 1) -> np.ndarray:
        """
        Permutation/Shift to represent sequences or order.
        We implement this by rotating the bits.
        """
        unpacked = np.unpackbits(v.view(np.uint8))
        shifted = np.roll(unpacked, places)
        return np.packbits(shifted).view(np.uint64)

    def popcount_distance(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculates Hamming distance using bitwise XOR and POPCNT.
        Returns the normalized distance (0.0 means identical, 0.5 means orthogonal).
        """
        xor_result = np.bitwise_xor(v1, v2)
        # NumPy doesn't have a native SIMD popcount for uint64 arrays in Python yet, 
        # but unpacking and summing is the mathematical equivalent.
        # In a C++ extension, we would use _mm256_popcnt_epi64.
        unpacked = np.unpackbits(xor_result.view(np.uint8))
        hamming_dist = np.sum(unpacked)
        return hamming_dist / float(self.dim)
        
    def similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Returns similarity (1.0 = identical, 0.0 = orthogonal)"""
        return 1.0 - (self.popcount_distance(v1, v2) * 2.0) # Scale so 0.5 dist = 0.0 sim

    def store_concept(self, name: str, vector: np.ndarray = None):
        if vector is None:
            vector = self._generate_random_vector()
        self.memory[name] = vector
        return vector

    def query(self, query_vec: np.ndarray, top_k: int = 3):
        """
        Queries the memory using POPCNT similarity.
        """
        results = []
        for name, memory_vec in self.memory.items():
            sim = self.similarity(query_vec, memory_vec)
            results.append((name, sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def reason(self, statement_vectors: list[np.ndarray], query_vector: np.ndarray):
        """
        Executes symbolic reasoning over a context.
        e.g. Bind (USA, Washington), Bind (France, Paris). Bundle into Knowledge.
        Query (France, Knowledge) -> Should unbind and return vector similar to Paris.
        """
        knowledge_base = self.bundle(statement_vectors)
        # Unbinding is also XOR in binary VSA
        unbound = self.bind(knowledge_base, query_vector)
        return self.query(unbound, top_k=1)
