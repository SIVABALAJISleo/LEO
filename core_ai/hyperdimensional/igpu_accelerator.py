"""
core_ai/hyperdimensional/igpu_accelerator.py
iGPU Bitwise Resonance Accelerator.
Uses PyOpenCL to parallelize XOR + Popcount (Hamming Distance) across the 48 EUs
of the Intel UHD Graphics.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

class IGPUAccelerator:
    def __init__(self):
        self.is_opencl_ready = False
        self.ctx = None
        self.queue = None
        self.prg = None
        
        try:
            import pyopencl as cl
            # Automatically find the Intel platform (preferably GPU)
            platforms = cl.get_platforms()
            intel_gpu = None
            
            for p in platforms:
                devices = p.get_devices(cl.device_type.GPU)
                if devices:
                    for d in devices:
                        if "Intel" in d.vendor or "Intel" in d.name:
                            intel_gpu = d
                            break
                if intel_gpu: break
                
            if intel_gpu:
                self.ctx = cl.Context([intel_gpu])
                self.queue = cl.CommandQueue(self.ctx)
                
                # OpenCL C Kernel for packed uint8 XOR + Popcount
                kernel_code = """
                __kernel void batch_hamming_distance(
                    __global const uchar* query,
                    __global const uchar* memory_matrix,
                    __global float* distances,
                    const int vec_len
                ) {
                    int gid = get_global_id(0);
                    int offset = gid * vec_len;
                    
                    int diff_count = 0;
                    for (int i = 0; i < vec_len; i++) {
                        uchar q = query[i];
                        uchar m = memory_matrix[offset + i];
                        uchar x = q ^ m;
                        // Popcount trick for 8-bit
                        diff_count += popcount((uint)x);
                    }
                    distances[gid] = (float)diff_count / (float)(vec_len * 8);
                }
                """
                self.prg = cl.Program(self.ctx, kernel_code).build()
                self.is_opencl_ready = True
                logger.info(f"[iGPU HDC] OpenCL initialized on: {intel_gpu.name}")
            else:
                logger.warning("[iGPU HDC] No Intel GPU found via OpenCL. Falling back to CPU AVX2.")
                
        except ImportError:
            logger.warning("[iGPU HDC] PyOpenCL not installed. Falling back to CPU AVX2.")
        except Exception as e:
            logger.warning(f"[iGPU HDC] OpenCL init failed: {e}. Falling back to CPU AVX2.")

    def calculate_hamming_distances(self, query_vec: np.ndarray, memory_matrix: np.ndarray) -> np.ndarray:
        """
        Calculates Hamming distance between a single query (1D) and a matrix of memory vectors (2D).
        Returns an array of floats [0.0, 1.0].
        """
        num_memories = memory_matrix.shape[0]
        vec_len = query_vec.shape[0]
        
        if self.is_opencl_ready:
            import pyopencl as cl
            mf = cl.mem_flags
            
            q_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=query_vec)
            m_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=memory_matrix)
            d_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, num_memories * 4) # float32
            
            distances = np.empty(num_memories, dtype=np.float32)
            
            self.prg.batch_hamming_distance(
                self.queue, (num_memories,), None,
                q_buf, m_buf, d_buf, np.int32(vec_len)
            )
            
            cl.enqueue_copy(self.queue, distances, d_buf).wait()
            return distances
            
        else:
            # Fallback to Colibri C-Engine or AVX2 if OpenCL is not ready
            from ..colibri_bridge import ColibriBridge
            bridge = ColibriBridge()
            return bridge.batch_hamming_distance(query_vec, memory_matrix)
