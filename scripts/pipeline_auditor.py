
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8005"

def run_phase_1():
    print("--- Phase 1: Pipeline Trace ---")
    payload = {"query": "What is the capital of France?"}
    try:
        response = requests.post(f"{BASE_URL}/api/orchestrate", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            trace = data.get("trace")
            with open("pipeline_trace.json", "w") as f:
                json.dump(trace, f, indent=2)
            print("Pipeline trace saved to pipeline_trace.json")
            
            # Check for reliability gap
            unreached = [layer for layer, info in trace.items() if not info["reached"]]
            if unreached:
                print(f"RELIABILITY GAP detected in layers: {unreached}")
                return False
            print("Pipeline trace successful. All layers reached.")
            return True
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def run_phase_2():
    print("\n--- Phase 2: Direct Engine Validation ---")
    try:
        response = requests.get(f"{BASE_URL}/debug/direct?q=hello", timeout=10)
        if response.status_code == 200:
            data = response.json()
            with open("engine_status.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Engine status saved to engine_status.json")
            if data["status"] == "success":
                print("Direct engine validation successful.")
                return True
            else:
                print(f"Engine Failure: {data.get('message')}")
                return False
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def run_phase_4():
    print("\n--- Phase 4: Response Stability Test ---")
    results = []
    success_count = 0
    for i in range(20):
        print(f"Query {i+1}/20...", end=" ", flush=True)
        try:
            payload = {"query": f"Is this query {i+1} stable?"}
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/orchestrate", json=payload, timeout=5)
            latency = time.time() - start_time
            if response.status_code == 200:
                print(f"PASS ({latency:.2f}s)")
                results.append({"query": i+1, "status": "success", "latency": latency})
                success_count += 1
            else:
                print(f"FAIL ({response.status_code})")
                results.append({"query": i+1, "status": "fail", "code": response.status_code})
        except Exception as e:
            print(f"CRASH ({e})")
            results.append({"query": i+1, "status": "crash", "error": str(e)})
        time.sleep(0.1)
    
    report = {
        "total": 20,
        "success": success_count,
        "fail": 20 - success_count,
        "pass_rate": success_count / 20,
        "results": results
    }
    with open("reliability_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nStability Pass Rate: {report['pass_rate']*100}%")
    return report["pass_rate"] >= 0.95

if __name__ == "__main__":
    p1 = run_phase_1()
    p2 = run_phase_2()
    
    if p1 and p2:
        print("\nReliability phases 1 & 2 passed.")
        p4 = run_phase_4()
        if p4:
            print("\nStability test PASSED.")
        else:
            print("\nStability test FAILED.")
    else:
        print("\nReliability phases 1 & 2 FAILED.")
