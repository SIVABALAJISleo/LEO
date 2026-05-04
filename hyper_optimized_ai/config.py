from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    APP_NAME: str = "HyperOptimizedAI"
    
    # Confidence Thresholds
    INPUT_GATE_CONFIDENCE_THRESHOLD: float = 0.8
    REALITY_FILTER_CONFIDENCE_THRESHOLD: float = 0.7
    ADAPTIVE_OUTPUT_HIGH_THRESHOLD: float = 0.85
    ADAPTIVE_OUTPUT_MEDIUM_THRESHOLD: float = 0.6
    
    # Confidence Engine Weights
    CONFIDENCE_WEIGHT_AGREEMENT: float = 0.4
    CONFIDENCE_WEIGHT_RECENCY: float = 0.3
    CONFIDENCE_WEIGHT_RELIABILITY: float = 0.3
    
    # Cache
    SEMANTIC_CACHE_THRESHOLD: float = 0.92
    
    # Models
    LLAMA_MODEL_PATH: str = "models/llama-2-7b-chat.Q4_K_M.gguf" 
    ONNX_MODEL_PATH: str = "models/tiny_model.onnx"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Paths
    FAISS_INDEX_PATH: str = "data/faiss_index"
    METADATA_PATH: str = "data/metadata.json"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
