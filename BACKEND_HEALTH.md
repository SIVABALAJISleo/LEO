# LEO backend — /health endpoint

The frontend pings `GET {VITE_LEO_API_BASE_URL}/health` every 15 seconds to
drive the connectivity badge on `/benchmarks` and Settings.

## Minimal FastAPI implementation

Add this to your Python backend (e.g. `main.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time, platform, os

app = FastAPI()

# CORS — required so the browser can call /health from the frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

START_TIME = time.time()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "leo-ai",
        "version": os.getenv("LEO_VERSION", "dev"),
        "uptime_sec": int(time.time() - START_TIME),
        "python": platform.python_version(),
    }
```

Start it on port 8005:

```bash
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

## Verify

```bash
curl http://localhost:8005/health
# → {"status":"ok","service":"leo-ai",...}
```

Then in the frontend Settings page pick a preset (Local / Tunnel / Deployed)
or paste the URL directly — the badge turns green when the response is 200
within 5 seconds.

## Tunneling to the Lovable preview

The preview runs in the cloud and cannot reach `localhost` on your laptop.
Use a tunnel:

```bash
# Cloudflare (no signup)
cloudflared tunnel --url http://localhost:8005

# or ngrok
ngrok http 8005
```

Paste the resulting `https://…` URL into the **Tunnel** field in Settings
and click the **Tunnel** preset. The badge on `/benchmarks` will confirm
live connectivity.
