import hashlib
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class InferenceCache:
    """
    Caches previous inference results, rendered media, and detection outputs.
    Follows CPU-first optimization by avoiding redundant computations.
    """
    def __init__(self, cache_file: str = "data/inference_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _generate_key(self, input_data: Any) -> str:
        input_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(input_str.encode()).hexdigest()

    def get(self, input_data: Any, namespace: str = "general") -> Optional[Any]:
        key = self._generate_key(f"{namespace}:{input_data}")
        result = self.cache.get(key)
        if result:
            logger.info(f"Cache hit for [{namespace}] key: {key[:8]}")
        return result

    def set(self, input_data: Any, result: Any, namespace: str = "general"):
        key = self._generate_key(f"{namespace}:{input_data}")
        self.cache[key] = result
        self._save_cache()
        logger.info(f"Cache set for [{namespace}] key: {key[:8]}")
        
    def cache_frame(self, frame_id: str, detections: Any):
        """Specifically cache vision detection results for a frame."""
        self.set(frame_id, detections, namespace="vision")
        
    def get_cached_scene(self, scene_id: str) -> Optional[Any]:
        """Specifically retrieve cached scene data."""
        return self.get(scene_id, namespace="scene")
