# Project HYPER SDK Usage Guide

Welcome to the official Python SDK for Project HYPER. Let your applications interact with the distributed cluster effortlessly.

## Installation

```bash
pip install hyper-sdk
```

## Initialization

Provide your API key to authenticate natively with the backend.

```python
from hyper_sdk import HyperClient

# Target production load balancers or local staging
client = HyperClient(api_key="sk_live_...", base_url="https://api.hyper.com/api/v1")
```

## Supported Engine Actions

### 1. Vision Analysis (YOLOv8)

```python
# Synchronous detection
results = client.vision.detect("https://example.com/car.jpg", confidence=0.7)
print(results)

# Asynchronous detection targeting a 5-second SLA
import asyncio
async def detect():
    res = await client.vision.detect_async("https://example.com/pedestrian.jpg")
    print(res)
```

### 2. Semantic Analysis (JEPA)

```python
results = client.jepa.compare(
    "https://example.com/img1.png",
    "https://example.com/img2.png"
)
print("Similarity Score:", results["feature_delta"])
```

### 3. Job & Queue Management

Interact directly with the Celery/Redis pool.

```python
job_id = "JOB_8892"

# Check execution bounds
status = client.jobs.status(job_id)
if status["status"] == "processing":
    print("Worker actively consuming CPU cycles...")

# Force Celery Revocation (Termination)
client.jobs.cancel(job_id)
```

## Fault Tolerance

The SDK natively implements `tenacity` exponential backoff.
If the API Gateway drops a packet or returns a 502/503 during a worker restart, the SDK will automatically seamlessly retry the connection up to 3 times before raising a `HyperAPIError`.
