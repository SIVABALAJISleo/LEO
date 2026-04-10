from typing import Any, Dict

class JobsClient:
    """SDK Wrapper for managing asynchronous Celery tasks queued in Redis."""
    
    def __init__(self, client: Any):
        self.client = client
        
    def status(self, job_id: str) -> Dict[str, Any]:
        """Retrieves the real-time execution bounds of a distributed job."""
        return self.client.request("GET", f"jobs/status/{job_id}")
        
    async def status_async(self, job_id: str) -> Dict[str, Any]:
        """Asynchronously retrieves the real-time execution bounds of a distributed job."""
        return await self.client.request_async("GET", f"jobs/status/{job_id}")
        
    def cancel(self, job_id: str) -> Dict[str, Any]:
        """Issues a revocation signal to the worker pool terminating the task execution."""
        return self.client.request("POST", f"jobs/{job_id}/cancel")
        
    async def cancel_async(self, job_id: str) -> Dict[str, Any]:
        """Asynchronously issues a revocation signal terminating the task execution."""
        return await self.client.request_async("POST", f"jobs/{job_id}/cancel")
