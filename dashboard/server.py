"""
dashboard/server.py
WebSocket metrics server for the PHOENIX RUNTIME real-time dashboard.
Broadcasts live telemetry every 500ms to connected browsers.
"""

import asyncio
import json
import time
import os
import sys
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import websockets

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
WS_PORT       = 8765
HTTP_PORT     = 8766


# ── Simulated telemetry (replace with PhoenixRuntime.get_runtime_stats()) ─────
class TelemetrySimulator:
    """Generates realistic-looking telemetry for demo when runtime isn't attached."""
    def __init__(self):
        import random
        self._r  = random
        self._t0 = time.time()
        self._tokens_generated = 0
        self._cache_hits = 0
        self._total_requests = 0
        self._route_counts = {"RULE_ENGINE": 0, "CALCULATOR": 0,
                              "RETRIEVAL_ENGINE": 0, "TINY_MODEL": 0,
                              "LARGE_MODEL": 0, "CACHE_HIT": 0}

    def tick(self) -> dict:
        import math, random
        elapsed = time.time() - self._t0

        # Simulate tokens/sec with some noise
        tps = 28 + 12 * math.sin(elapsed * 0.3) + random.uniform(-3, 3)
        tps = max(5, tps)
        self._tokens_generated += int(tps * 0.5)

        # Simulate new requests
        new_req = random.choices(
            list(self._route_counts.keys()),
            weights=[20, 5, 15, 25, 20, 15], k=random.randint(0, 2)
        )
        for r in new_req:
            self._route_counts[r] += 1
            self._total_requests  += 1
            if r == "CACHE_HIT":
                self._cache_hits += 1

        cache_rate = self._cache_hits / max(1, self._total_requests) * 100

        return {
            "timestamp":           round(elapsed, 1),
            "tokens_per_sec":      round(tps, 1),
            "total_tokens":        self._tokens_generated,
            "total_requests":      self._total_requests,
            "cache_hit_rate_pct":  round(cache_rate, 1),
            "cpu_percent":         round(30 + 20 * abs(math.sin(elapsed * 0.2)) + random.uniform(0,5), 1),
            "ram_percent":         round(68 + 5  * math.sin(elapsed * 0.1)  + random.uniform(0,2), 1),
            "early_exit_savings":  round(55 + 10 * math.sin(elapsed * 0.15) + random.uniform(0,5), 1),
            "avg_latency_ms":      round(max(1, 45 - tps * 0.5 + random.uniform(-5,5)), 1),
            "active_experts":      random.randint(2, 4),
            "kv_cache_used_pct":   round(min(95, elapsed * 0.5 + random.uniform(0, 10)), 1),
            "route_distribution":  dict(self._route_counts),
        }


_telemetry = TelemetrySimulator()
_connected_clients = set()


async def ws_handler(websocket):
    _connected_clients.add(websocket)
    logger.info(f"Dashboard client connected. Total: {len(_connected_clients)}")
    try:
        async for _ in websocket:
            pass   # We only push, no incoming messages needed
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        _connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(_connected_clients)}")


async def broadcast_loop():
    while True:
        if _connected_clients:
            data = _telemetry.tick()
            msg  = json.dumps(data)
            dead = set()
            for ws in _connected_clients:
                try:
                    await ws.send(msg)
                except Exception:
                    dead.add(ws)
            _connected_clients -= dead
        await asyncio.sleep(0.5)


def run_http_server():
    os.chdir(DASHBOARD_DIR)
    server = HTTPServer(("localhost", HTTP_PORT), SimpleHTTPRequestHandler)
    logger.info(f"Dashboard HTTP server: http://localhost:{HTTP_PORT}")
    server.serve_forever()


async def main():
    # Start HTTP server in background thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server
    logger.info(f"WebSocket server: ws://localhost:{WS_PORT}")
    async with websockets.serve(ws_handler, "localhost", WS_PORT):
        await broadcast_loop()


if __name__ == "__main__":
    print("🔥 PHOENIX RUNTIME Dashboard")
    print(f"   Open: http://localhost:{HTTP_PORT}")
    print(f"   WebSocket: ws://localhost:{WS_PORT}")
    asyncio.run(main())
