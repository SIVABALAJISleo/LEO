import re

with open(r"c:\Users\sivab\OneDrive\Documents\HYPER\remix-of-remix-of-remix-of-nvidia-inspired-design-main\backend\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add a /metrics endpoint if it's not there
metrics_route = """
@app.get("/metrics")
async def get_metrics():
    from backend.analytics.metrics import global_metrics
    return global_metrics.get_metrics()
"""

if "/metrics" not in code:
    code += "\n" + metrics_route + "\n"
    with open(r"c:\Users\sivab\OneDrive\Documents\HYPER\remix-of-remix-of-remix-of-nvidia-inspired-design-main\backend\main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Metrics endpoint added to main.py")
else:
    print("Metrics endpoint already in main.py")