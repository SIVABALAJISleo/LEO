from typing import Any, Dict

class JEPAClient:
    """SDK Wrapper for Project HYPER JEPA operations."""
    
    def __init__(self, client: Any):
        self.client = client
        
    def compare(self, image_url_1: str, image_url_2: str) -> Dict[str, Any]:
        """Executes Joint Embedding Predictive Architecture comparison between two images."""
        payload = {
            "image_url_1": image_url_1, 
            "image_url_2": image_url_2
        }
        return self.client.request("POST", "jepa/compare", json=payload)
        
    async def compare_async(self, image_url_1: str, image_url_2: str) -> Dict[str, Any]:
        """Asynchronously executes JEPA comparison between two images."""
        payload = {
            "image_url_1": image_url_1, 
            "image_url_2": image_url_2
        }
        return await self.client.request_async("POST", "jepa/compare", json=payload)
