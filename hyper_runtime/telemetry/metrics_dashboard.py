import json
import os

def generate_html_report(metrics_file):
    if not os.path.exists(metrics_file):
        print("No metrics found.")
        return
        
    hits = 0
    total = 0
    total_latency = 0
    
    with open(metrics_file, 'r') as f:
        for line in f:
            if not line.strip(): continue
            m = json.loads(line)
            total += 1
            if m.get("source") == "semantic_cache":
                hits += 1
            total_latency += m.get("latency", 0)
            
    hit_rate = (hits / total) * 100 if total > 0 else 0
    avg_latency = (total_latency / total) if total > 0 else 0
    
    html = f"""
    <html>
    <head><title>HYPER Metrics</title></head>
    <body style="font-family: sans-serif; padding: 20px;">
        <h1>HYPER Telemetry Dashboard</h1>
        <div style="display: flex; gap: 20px;">
            <div style="padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
                <h3>Cache Hit Rate</h3>
                <p style="font-size: 24px; color: green;">{hit_rate:.1f}%</p>
            </div>
            <div style="padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
                <h3>Avg Latency</h3>
                <p style="font-size: 24px;">{avg_latency:.3f} s</p>
            </div>
            <div style="padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
                <h3>Total Queries</h3>
                <p style="font-size: 24px;">{total}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("dashboard.html", "w") as f:
        f.write(html)
    print("Dashboard generated: dashboard.html")

if __name__ == "__main__":
    generate_html_report("metrics.jsonl")
