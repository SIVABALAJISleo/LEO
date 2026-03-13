import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Compute-Avoidance Intelligence System"
    API_V1_STR: str = "/api/v1"
    
    # Redis for Cache & Celery
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    # Vector DB settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "data/faiss_index.bin"
    
    # Thresholds
    CONFIDENCE_THRESHOLD: float = 0.7
    REUSE_SIMILARITY_THRESHOLD: float = 0.95

    class Config:
        case_sensitive = True

settings = Settings()
