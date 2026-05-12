from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "ClosedLoopSynthesis"
    
    # Synthesis Loop
    MAX_ITERATIONS: int = 10
    CANDIDATES_PER_ITER: int = 3
    TIMEOUT_SECONDS: int = 5
    MEMORY_LIMIT_MB: int = 512
    
    # Models
    PROPOSER_MODEL_PATH: str = "models/phi-3-mini-4k-instruct-q4.gguf"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Cache
    CACHE_THRESHOLD: float = 0.95
    CACHE_INDEX_PATH: str = "data/synthesis_cache/index.faiss"
    CACHE_METADATA_PATH: str = "data/synthesis_cache/metadata.json"
    
    # Sandbox
    SANDBOX_DIR: str = "sandbox"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs(settings.SANDBOX_DIR, exist_ok=True)
