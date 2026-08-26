import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from leo_engine import LEOv7_MemoryEfficient

def run_real_benchmark():
    leo = LEOv7_MemoryEfficient()
    leo.initialize_cache()
    
    # Test queries: SEMANTIC VARIANTS of cached FAQs
    # These are NOT in cache, but semantically similar
    test_queries = [
        # Variant of "How do I reset my password?"
        "I forgot my password, what do I do?",
        
        # Variant of "What's the VPN setup?"
        "How do I connect to company VPN?",
        
        # Variant of "How do I request a laptop?"
        "Need a new computer, what's the process?",
        
        # Variant of "How do I connect to printer?"
        "Can't print, how do I add a printer?",
        
        # COMPLETELY NEW query (not in cache)
        "What's the best coffee in the office?",
    ]
    
    print("\n" + "="*70)
    print("LEO v7 REAL BENCHMARK - i5-12450H, 16GB RAM")
    print("="*70 + "\n")
    
    leo.run_benchmark(test_queries, "Testing Semantic Cache + LLM Fallback")

if __name__ == "__main__":
    run_real_benchmark()
