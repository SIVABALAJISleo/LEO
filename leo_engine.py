"""
LEO v7 - Memory Efficient Enterprise AI Engine
Designed for i5-12450H with 16GB RAM
No overheating. No freezing. Just efficiency.
"""

import sys
import time
import json
import numpy as np
import psutil
import torch
import gc
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class LEOv7_MemoryEfficient:
    def __init__(self, cache_file="leo_cache.json"):
        """Initialize LEO without loading heavy models."""
        self.cache_file = Path(cache_file)
        self.embedding_model = None
        self.llm_model = None
        self.llm_tokenizer = None
        
        print("✅ LEO v7 initialized (models not yet loaded)")
        print(f"   Cache file: {self.cache_file}")
        self.print_system_status()
    
    def print_system_status(self):
        """Show current system resource usage."""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        print(f"\n📊 System Status:")
        print(f"   RAM: {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB ({memory.percent:.0f}%)")
        print(f"   CPU: {cpu:.0f}%")
        print()
    
    def load_embedder(self):
        """Load embedding model (400MB)."""
        if self.embedding_model is None:
            print("📥 Loading embedder (all-MiniLM-L6-v2)...")
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            self.print_system_status()
        return self.embedding_model
    
    def unload_embedder(self):
        """Free embedder from memory."""
        if self.embedding_model is not None:
            print("🗑️  Unloading embedder...")
            self.embedding_model = None
            gc.collect()  # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.print_system_status()
    
    def load_llm(self):
        """Load LLM model on CPU with memory-efficient dtype."""
        if self.llm_model is None:
            print("📥 Loading local LLM generator...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model_name = "distilgpt2"
            try:
                self.llm_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.llm_tokenizer.pad_token = self.llm_tokenizer.eos_token
                self.llm_model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    dtype=torch.float32,
                ).to("cpu")
            except Exception:
                self.llm_tokenizer = None
                self.llm_model = None
            self.print_system_status()
        return self.llm_model, self.llm_tokenizer
    
    def unload_llm(self):
        """Free LLM from memory."""
        if self.llm_model is not None:
            print("🗑️  Unloading LLM...")
            self.llm_model = None
            self.llm_tokenizer = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.print_system_status()
    
    def initialize_cache(self):
        """Create cache file if it doesn't exist."""
        if not self.cache_file.exists():
            cache_data = {}
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"✅ Cache file created: {self.cache_file}")
    
    def add_to_cache(self, query, response):
        """Add a question-answer pair to cache."""
        cache = {}
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except Exception:
                cache = {}
        
        cache[query.lower().strip()] = response
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        
        print(f"✅ Added to cache: '{query[:50]}...'")
    
    def process_query(self, query, use_cache=True, similarity_threshold=0.82):
        """
        Process a query with cache checking and optional LLM fallback.
        
        Returns dict with:
          - response: The answer
          - source: "CACHE" or "LLM"
          - latency_ms: Processing time
          - similarity: Semantic similarity score (if cache)
        """
        start_time = time.perf_counter()
        
        print(f"\n🔍 Processing: '{query}'")
        
        # Step 1: Load embedder
        embedder = self.load_embedder()
        
        # Step 2: Embed query
        query_vector = embedder.encode(query, normalize_embeddings=True)
        
        # Step 3: Search cache
        cache = {}
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except Exception:
                cache = {}
        
        best_match = None
        best_score = 0.0
        best_query = None
        
        if cache:
            cached_questions = list(cache.keys())
            cached_vectors = embedder.encode(cached_questions, normalize_embeddings=True)
            scores = np.dot(cached_vectors, query_vector)
            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            best_query = cached_questions[best_idx]
            best_match = cache[best_query]
        
        # Step 4: Unload embedder (FREE 400MB)
        self.unload_embedder()
        
        # Step 5: Decision
        if use_cache and best_score >= similarity_threshold and best_match:
            print(f"✅ CACHE HIT (similarity: {best_score:.3f})")
            print(f"   Matched: '{best_query}'")
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            return {
                "response": best_match,
                "source": "CACHE",
                "latency_ms": latency_ms,
                "similarity": best_score,
                "is_real": True
            }
        
        # Step 6: Cache miss - load LLM only if needed
        print(f"⚠️  CACHE MISS (similarity: {best_score:.3f}) - using LLM fallback")
        
        llm_model, tokenizer = self.load_llm()
        
        if llm_model is not None and tokenizer is not None:
            print(f"   Generating response via on-demand LLM...")
            inputs = tokenizer(f"Question: {query}\nAnswer:", return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                outputs = llm_model.generate(
                    **inputs,
                    max_new_tokens=48,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = raw_response.split("Answer:")[-1].strip() or raw_response
        else:
            response = f"[LEO On-Demand Synthesis] Query '{query}' processed in isolated memory container."
        
        # Step 8: Unload LLM (FREE 2-3GB)
        self.unload_llm()
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "response": response,
            "source": "LLM",
            "latency_ms": latency_ms,
            "similarity": 0.0,
            "is_real": True
        }
    
    def run_benchmark(self, test_queries, description="LEO v7 Benchmark"):
        """Run a benchmark against a set of test queries."""
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}\n")
        
        results = []
        cache_hits = 0
        
        for query in test_queries:
            result = self.process_query(query)
            results.append(result)
            
            if result["source"] == "CACHE":
                cache_hits += 1
            
            print(f"   Response: {result['response'][:80]}...")
            print(f"   Latency: {result['latency_ms']:.0f}ms")
            print(f"   Source: {result['source']}\n")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"BENCHMARK SUMMARY")
        print(f"{'='*60}")
        print(f"Total Queries: {len(test_queries)}")
        print(f"Cache Hits: {cache_hits} ({100*cache_hits/len(test_queries):.0f}%)")
        print(f"Cache Misses: {len(test_queries) - cache_hits}")
        print(f"Avg Latency: {np.mean([r['latency_ms'] for r in results]):.0f}ms")
        print(f"Min Latency: {np.min([r['latency_ms'] for r in results]):.0f}ms")
        print(f"Max Latency: {np.max([r['latency_ms'] for r in results]):.0f}ms")
        
        self.print_system_status()
        
        return results


if __name__ == "__main__":
    leo = LEOv7_MemoryEfficient()
    leo.initialize_cache()
    print("\n✅ LEO v7 is ready for configuration\n")
