import os
import multiprocessing
from pydantic_settings import BaseSettings

class HyperConfig(BaseSettings):
    # App General
    app_env: str = "development"
    
    # Compute Nodes & Workers
    MAX_WORKERS: int = max(1, multiprocessing.cpu_count() - 1)
    
    # Distributed Architecture Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "hyper-saas-bucket")
    
    # LLM Settings
    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", "models/llama-2-7b-chat.Q4_K_M.gguf")
    LLM_THREADS: int = max(1, multiprocessing.cpu_count() // 2)
    LLM_BATCH_SIZE: int = 512
    LLM_CONTEXT_WINDOW: int = 4096
    
    # Video & Render Settings
    RENDER_THREADS: int = max(1, multiprocessing.cpu_count() // 2)
    FFMPEG_PRESET: str = "fast"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    FFMPEG_CRF: int = 23
    
    # HPC Optimization Features
    PERFORMANCE_MODE: str = os.getenv("PERFORMANCE_MODE", "Balanced")
    ENABLE_ISPC_KERNELS: bool = os.getenv("ENABLE_ISPC_KERNELS", "true").lower() == "true"
    ENABLE_TVM_AUTOTUNE: bool = os.getenv("ENABLE_TVM_AUTOTUNE", "true").lower() == "true"
    QUANTIZATION_LEVEL: str = os.getenv("QUANTIZATION_LEVEL", "INT8")
    SPARSE_MATRIX_KERNELS: bool = os.getenv("SPARSE_MATRIX_KERNELS", "true").lower() == "true"
    WINOGRAD_CONV: bool = os.getenv("WINOGRAD_CONV", "true").lower() == "true"
    ENABLE_IGPU_ACCEL: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = HyperConfig()
