import logging
import numpy as np
import time
from typing import Callable, Tuple, List
try:
    from numba import njit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    # Fallback to no-op decorators
    def njit(*args, **kwargs): return lambda f: f
    prange = range

logger = logging.getLogger(__name__)

@njit(fastmath=True)
def sphere_sdf_jit(p, center, radius):
    # p is (3,), center is (3,)
    diff = p - center
    return np.sqrt(np.sum(diff**2)) - radius

@njit(fastmath=True)
def box_sdf_jit(p, center, size):
    q = np.abs(p - center) - size
    # Outer distance
    outer = np.sqrt(np.sum(np.maximum(q, 0.0)**2))
    # Inner distance
    inner = np.minimum(np.maximum(q[0], np.maximum(q[1], q[2])), 0.0)
    return outer + inner

@njit(fastmath=True)
def map_scene_jit(p, time_sec):
    # Sphere
    s_center = np.array([np.sin(time_sec), 0.5, 0.0])
    d1 = sphere_sdf_jit(p, s_center, 0.6)
    
    # Floor Box
    b_center = np.array([0.0, -1.0, 0.0])
    b_size = np.array([2.0, 0.1, 2.0])
    d2 = box_sdf_jit(p, b_center, b_size)
    
    return np.minimum(d1, d2)

@njit(fastmath=True, parallel=True)
def raymarch_kernel(height, width, camera_pos, ray_dirs, time_sec, max_steps=40):
    t_vals = np.zeros((height, width))
    hit_mask = np.zeros((height, width), dtype=np.bool_)
    
    for i in prange(height):
        for j in range(width):
            t = 0.0
            ro = camera_pos
            rd = ray_dirs[i, j]
            
            for _ in range(max_steps):
                p = ro + t * rd
                dist = map_scene_jit(p, time_sec)
                
                if dist < 0.005:
                    hit_mask[i, j] = True
                    break
                
                t += dist
                if t > 15.0:
                    break
            
            t_vals[i, j] = t
            
    return t_vals, hit_mask

class SDFRenderer:
    """
    CPU-Native SDF Raymarching Visual Engine.
    JIT-Optimized for high-performance CPU rendering.
    """
    def __init__(self, width: int = 256, height: int = 144):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        # Precompute coordinate grid
        u = np.linspace(-self.aspect_ratio, self.aspect_ratio, self.width)
        v = np.linspace(-1, 1, self.height)
        U, V = np.meshgrid(u, v)
        self.U = U
        self.V = V
        
        # Precompute ray directions
        self.ray_dirs = np.stack([U, -V - 0.2, np.ones_like(U) * 1.5], axis=-1).astype(np.float64)
        for i in range(height):
            for j in range(width):
                self.ray_dirs[i, j] /= np.linalg.norm(self.ray_dirs[i, j])
                
        self.camera_pos = np.array([0.0, 1.0, -4.0], dtype=np.float64)
        
        if HAS_NUMBA:
            logger.info(f"SDFRenderer initialized at {width}x{height} (JIT-ACCELERATED)")
        else:
            logger.warning(f"SDFRenderer initialized at {width}x{height} (NUMBA MISSING - SLOW)")

    def render_frame(self, time_sec: float) -> np.ndarray:
        t_vals, hit_mask = raymarch_kernel(self.height, self.width, self.camera_pos, self.ray_dirs, time_sec)

        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Simple Lighting (Vectorized on the result)
        if np.any(hit_mask):
            # Normal calculation and lighting can also be JITed if needed, 
            # but usually the raymarching loop is 99% of the cost.
            # Keeping it in NumPy for now for readability unless profiling says otherwise.
            e = 0.001
            # Note: We compute normals only for hit pixels
            # To keep it simple and vectorized with NumPy, we'll do it for all then mask
            p = self.camera_pos + t_vals[..., None] * self.ray_dirs
            
            # Approximate normals
            dx = np.zeros_like(t_vals)
            dy = np.zeros_like(t_vals)
            dz = np.zeros_like(t_vals)
            
            # Only compute for hit mask to save time
            hit_p = p[hit_mask]
            dx_h = map_scene_jit(hit_p + np.array([e, 0, 0]), time_sec) - map_scene_jit(hit_p - np.array([e, 0, 0]), time_sec)
            dy_h = map_scene_jit(hit_p + np.array([0, e, 0]), time_sec) - map_scene_jit(hit_p - np.array([0, e, 0]), time_sec)
            dz_h = map_scene_jit(hit_p + np.array([0, 0, e]), time_sec) - map_scene_jit(hit_p - np.array([0, 0, e]), time_sec)
            
            normal_h = np.stack([dx_h, dy_h, dz_h], axis=-1)
            norm_h = np.sqrt(np.sum(normal_h**2, axis=-1, keepdims=True)) + 1e-6
            normal_h /= norm_h
            
            light_dir = np.array([0.5, 1.0, -0.5])
            light_dir /= np.linalg.norm(light_dir)
            diffuse_h = np.maximum(0.1, np.sum(normal_h * light_dir, axis=-1))
            
            attenuation_h = 1.0 / (1.0 + t_vals[hit_mask] * 0.1)
            color_h = np.array([0, 180, 255]) * diffuse_h[..., None] * attenuation_h[..., None]
            image[hit_mask] = color_h.astype(np.uint8)

        # Background gradient
        bg_mask = ~hit_mask
        if np.any(bg_mask):
            bg_v = self.V[bg_mask]
            bg_colors = (np.array([15, 15, 25]) * (1.2 - np.abs(bg_v[..., None]))).astype(np.uint8)
            image[bg_mask] = bg_colors
        
        return image

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    renderer = SDFRenderer()
    
    # Warmup
    renderer.render_frame(0.0)
    
    start = time.time()
    for _ in range(10):
        renderer.render_frame(0.0)
    duration = (time.time() - start) / 10
    print(f"Average render time (JIT): {duration:.4f}s ({1/duration:.1f} FPS)")


