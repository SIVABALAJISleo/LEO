import time
from speculative_decoder import SpeculativeDecoder

class MockModel:
    def __init__(self, latency):
        self.latency = latency
    def speculate(self, ids, k):
        time.sleep(self.latency * k)
        return [100, 101, 102, 103][:k]
    def forward(self, ids):
        time.sleep(self.latency)
        class Logit:
            def argmax(self): return 100
        return [Logit() for _ in range(len(ids))]

def run():
    target = MockModel(0.050)
    draft = MockModel(0.005)
    
    decoder = SpeculativeDecoder(target, draft, k=3)
    
    print("Benchmarking Speculative Decoding...")
    start = time.time()
    out, accepted = decoder.generate([1,2,3], max_tokens=10)
    end = time.time()
    
    print(f"Generated {len(out)-3} tokens in {end-start:.2f}s")
    print(f"Accepted Draft Tokens: {accepted}")
    print(f"Effective Throughput: {(len(out)-3)/(end-start):.2f} tok/s")

if __name__ == "__main__":
    run()
