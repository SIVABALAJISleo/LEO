import httpx
from typing import Dict, Any, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from .vision import VisionClient
from .jepa import JEPAClient
from .jobs import JobsClient

class HyperAPIError(Exception):
    pass

class HyperClient:
    """Official Python SDK for Project HYPER Enterprise AI Platform."""
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "http://localhost:8000/api/v1"
    ):
        if not api_key:
            raise ValueError("API key must be provided")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize sub-clients
        self.vision = VisionClient(self)
        self.jepa = JEPAClient(self)
        self.jobs = JobsClient(self)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Synchronous request with exponential backoff on network failures."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        with httpx.Client(headers=self._headers, timeout=30.0) as client:
            response = client.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                raise HyperAPIError(f"API Error {response.status_code}: {response.text}")
                
            response.raise_for_status()
            return response.json()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def request_async(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Asynchronous request with exponential backoff on network failures."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            response = await client.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                raise HyperAPIError(f"API Error {response.status_code}: {response.text}")
                
            response.raise_for_status()
            return response.json()
