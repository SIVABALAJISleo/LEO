from typing import Any, Dict

class VisionClient:
    """SDK Wrapper for Project HYPER Vision AI operations."""
    
    def __init__(self, client: Any):
        # We pass the parent HyperClient instance to utilize its authenticated `request` methods.
        self.client = client
        
    def detect(self, image_url: str, confidence: float = 0.5) -> Dict[str, Any]:
        """Runs YOLOv8 object detection on the provided image."""
        payload = {"image_url": image_url, "confidence": confidence}
        return self.client.request("POST", "vision/detect", json=payload)
        
    async def detect_async(self, image_url: str, confidence: float = 0.5) -> Dict[str, Any]:
        """Asynchronously runs YOLOv8 object detection on the provided image."""
        payload = {"image_url": image_url, "confidence": confidence}
        return await self.client.request_async("POST", "vision/detect", json=payload)
        
    def caption(self, image_url: str) -> Dict[str, Any]:
        """Runs BLIP-2 image captioning on the provided image."""
        payload = {"image_url": image_url}
        return self.client.request("POST", "vision/caption", json=payload)
        
    async def caption_async(self, image_url: str) -> Dict[str, Any]:
        """Asynchronously runs BLIP-2 image captioning on the provided image."""
        payload = {"image_url": image_url}
        return await self.client.request_async("POST", "vision/caption", json=payload)
