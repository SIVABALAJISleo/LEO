import time
import requests

def run_ray_logic_benchmark():
    url = "http://localhost:8005/api/orchestrate"
    payload = {"query": "Render high-fidelity scene with complex lighting"}
    
    print("--- SDGP Ray-Logic Benchmark ---")
    start = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=5)
        data = resp.json()
        end = time.time()
        
        if resp.status_code == 200:
            bt = data.get("breakthrough", {})
            print(f"Status: SUCCESS")
            print(f"Total Turnaround: {(end - start)*1000:.2f}ms")
            print(f"SDGP Latency: {bt.get('sdgp_latency_ms'):.2f}ms")
            print(f"Ray-Logic Depth: {bt.get('ray_logic_depth')}")
            print(f"Perceptual Culling: {bt.get('perceptual_culling')}")
            print(f"DLSS-S Active: {bt.get('dlss_s_active')}")
            print(f"Hardware Relevance: {bt.get('gpu_relevance_reduction')}")
            
            # Validation Logic
            if bt.get("gpu_relevance_reduction") == "100.00%":
                print("\nVALIDATION: PASSED (100% Software-Defined)")
            else:
                print("\nVALIDATION: FAILED (Hardware leakage detected)")
        else:
            print(f"Status: FAILED ({resp.status_code})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_ray_logic_benchmark()
