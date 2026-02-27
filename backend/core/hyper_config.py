import os
import multiprocessing
from pydantic_settings import BaseSettings

class HyperConfig(BaseSettings):
    # App General
    app_env: str = "development"
    
    # Compute Nodes & Workers
    MAX_WORKERS: int = max(1, multiprocessing.cpu_count() - 1)
    
    # LLM Settings
    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", "models/llama-2-7b-chat.Q4_K_M.gguf")
    LLM_THREADS: int = max(1, multiprocessing.cpu_count() // 2)
    LLM_BATCH_SIZE: int = 512
    LLM_CONTEXT_WINDOW: int = 4096
    
    # Video & Render Settings
    RENDER_THREADS: int = max(1, multiprocessing.cpu_count() // 2)
    FFMPEG_PRESET: str = "fast"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    FFMPEG_CRF: int = 23
    
    # Performance Features
    ENABLE_IGPU_ACCEL: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = HyperConfig()
