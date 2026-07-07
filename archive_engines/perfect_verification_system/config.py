from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "PerfectVerificationSystem"
    
    # Thresholds
    MIN_COVERAGE: float = 0.85
    MIN_MUTATION_SCORE: float = 0.90
    CACHE_THRESHOLD: float = 0.92
    
    # Loop Settings
    MAX_CANDIDATES: int = 5
    ADAPTIVE_ITER_MAX: int = 15
    TIMEOUT_SECONDS: int = 15
    
    # Paths
    SANDBOX_DIR: str = "sandbox_extreme"
    CACHE_DIR: str = "data/perfect_cache"
    MODEL_PATH: str = "models/phi-3-mini-4k-instruct-q4.gguf"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs(settings.SANDBOX_DIR, exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)
