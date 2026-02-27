import requests
import time
import threading

def fetch(url):
    start = time.time()
    try:
        response = requests.get(url)
        latency = time.time() - start
        return latency
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    url = "http://localhost:8005/health"
    threads = []
    latencies = []
    
    def worker():
        lat = fetch(url)
        if lat: latencies.append(lat)

    start_total = time.time()
    for _ in range(50):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        print(f"Avg Latency for 50 concurrent users: {avg_lat*1000:.2f}ms")
    print(f"Total test time: {time.time() - start_total:.2f}s")

if __name__ == "__main__":
    main()
