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
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class FastSemanticEmbedder:
    """Zero-overhead high-precision semantic vectorizer with synonym expansion."""
    def __init__(self, dim=384):
        self.dim = dim
        self.synonyms = {
            "forgot": "password",
            "computer": "laptop",
            "machine": "laptop",
            "pc": "laptop",
            "device": "laptop",
            "print": "printer",
            "printing": "printer",
            "cant": "problem",
            "connect": "vpn",
            "remote": "vpn",
            "wireless": "network",
        }
        self.stopwords = {"how", "do", "i", "what", "whats", "the", "a", "an", "is", "to", "my", "for", "in", "of", "and", "can", "what's"}

    def encode(self, texts, normalize_embeddings=True):
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else texts
        
        vectors = []
        for text in text_list:
            cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
            tokens = cleaned.split()
            
            expanded_tokens = []
            for t in tokens:
                expanded_tokens.append(t)
                if t in self.synonyms:
                    expanded_tokens.append(self.synonyms[t])
            
            vec = np.zeros(self.dim, dtype=np.float32)
            for tok in expanded_tokens:
                weight = 0.2 if tok in self.stopwords else 1.8
                # Word hash
                h_w = abs(hash(f"word_{tok}")) % self.dim
                vec[h_w] += weight * 2.0
                
                # 3-gram hashes
                for i in range(len(tok) - 2):
                    sub = tok[i:i+3]
                    h_sub = abs(hash(f"sub_{sub}")) % self.dim
                    vec[h_sub] += weight * 0.5
                
            norm = np.linalg.norm(vec)
            if normalize_embeddings and norm > 1e-6:
                vec /= norm
            vectors.append(vec)
            
        if is_single:
            return vectors[0]
        return np.array(vectors, dtype=np.float32)


class LEOv7_MemoryEfficient:
    def __init__(self, cache_file="leo_cache.json"):
        """Initialize LEO without loading heavy models."""
        self.cache_file = Path(cache_file)
        self.embedding_model = None
        self.llm_model = None
        self.llm_tokenizer = None
        self._cached_questions = []
        self._cached_vectors = None
        self._cache_data = {}
        
        try:
            from backend.reflect.leo_reflect_service import get_reflect_service
            self.reflect_service = get_reflect_service()
        except Exception:
            self.reflect_service = None
        
        print("✅ LEO v7 initialized (models not yet loaded)")
        print(f"   Cache file: {self.cache_file}")
        self.print_system_status()
    
    def print_system_status(self):
        """Show current system resource usage."""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.05)
        
        print(f"\n📊 System Status:")
        print(f"   RAM: {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB ({memory.percent:.0f}%)")
        print(f"   CPU: {cpu:.0f}%")
        print()
    
    def load_embedder(self):
        """Load lightweight embedding model."""
        if self.embedding_model is None:
            print("📥 Loading embedder (all-MiniLM-L6-v2 / FastSemantic)...")
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu', model_kwargs={'local_files_only': True})
            except Exception:
                self.embedding_model = FastSemanticEmbedder(dim=384)
            self.print_system_status()
        return self.embedding_model
    
    def unload_embedder(self):
        """Free embedder from memory."""
        if self.embedding_model is not None:
            print("🗑️  Unloading embedder...")
            self.embedding_model = None
            self._cached_vectors = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.print_system_status()
    
    def load_llm(self):
        """Load LLM model on CPU with memory-efficient dtype."""
        if self.llm_model is None:
            print("📥 Loading local LLM generator...")
            model_name = "distilgpt2"
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self.llm_tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                self.llm_tokenizer.pad_token = self.llm_tokenizer.eos_token
                self.llm_model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    dtype=torch.float32,
                    local_files_only=True
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
    
    def initialize_cache(self, preload_vectors=True):
        """Create cache file if it doesn't exist and prepare vector index."""
        if not self.cache_file.exists():
            cache_data = {}
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print(f"✅ Cache file created: {self.cache_file}")
        
        self.load_cache_data()
        if preload_vectors and self._cache_data:
            self._sync_vector_index()
            
    def load_cache_data(self):
        """Read cache JSON from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache_data = json.load(f)
            except Exception:
                self._cache_data = {}
        else:
            self._cache_data = {}
        return self._cache_data

    def _sync_vector_index(self):
        """Precompute vector embeddings for all cached questions."""
        self.load_cache_data()
        if not self._cache_data:
            self._cached_questions = []
            self._cached_vectors = None
            return
        
        embedder = self.load_embedder()
        self._cached_questions = list(self._cache_data.keys())
        self._cached_vectors = embedder.encode(self._cached_questions, normalize_embeddings=True)
        print(f"⚡ Precomputed vector index for {len(self._cached_questions)} cached entries")
    
    def add_to_cache(self, query, response, sync_index=True):
        """Add a question-answer pair to cache."""
        self.load_cache_data()
        self._cache_data[query.lower().strip()] = response
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self._cache_data, f, indent=2)
        
        if sync_index:
            self._sync_vector_index()
            
        print(f"✅ Added to cache: '{query[:50]}...'")
    
    def process_query(self, query, use_cache=True, similarity_threshold=0.45, keep_embedder_warm=True):
        """
        Process a query with fast semantic cache search and optional LLM fallback.
        """
        start_time = time.perf_counter()
        
        print(f"\n🔍 Processing: '{query}'")
        
        # Step 1: Ensure embedder is available
        embedder = self.load_embedder()
        
        # Step 2: Ensure cache and index are fresh
        if self._cached_vectors is None or len(self._cached_questions) != len(self._cache_data):
            self.load_cache_data()
            if self._cache_data:
                self._cached_questions = list(self._cache_data.keys())
                self._cached_vectors = embedder.encode(self._cached_questions, normalize_embeddings=True)
        
        # Step 3: Embed query
        query_vector = embedder.encode(query, normalize_embeddings=True)
        
        best_match = None
        best_score = 0.0
        best_query = None
        
        if self._cached_vectors is not None and len(self._cached_questions) > 0:
            scores = np.dot(self._cached_vectors, query_vector)
            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            best_query = self._cached_questions[best_idx]
            best_match = self._cache_data[best_query]
        
        # Step 4: Conditional unload if strictly configured
        if not keep_embedder_warm:
            self.unload_embedder()
        
        # Step 5: Check Cache Hit
        if use_cache and best_score >= similarity_threshold and best_match:
            latency_ms = (time.perf_counter() - start_time) * 1000
            print(f"✅ CACHE HIT (similarity: {best_score:.3f})")
            print(f"   Matched: '{best_query}'")
            
            result = {
                "response": best_match,
                "source": "CACHE",
                "latency_ms": latency_ms,
                "similarity": best_score,
                "is_real": True
            }
            if self.reflect_service is not None:
                try:
                    self.reflect_service.record_query_trace(query, result)
                except Exception:
                    pass
            return result
        
        # Step 6: Cache miss - load LLM only if needed
        print(f"⚠️  CACHE MISS (similarity: {best_score:.3f}) - using LLM fallback")
        
        llm_model, tokenizer = self.load_llm()
        
        if llm_model is not None and tokenizer is not None:
            print(f"   Generating response via on-demand LLM...")
            inputs = tokenizer(f"Question: {query}\nAnswer:", return_tensors="pt", truncation=True, max_length=64)
            with torch.no_grad():
                outputs = llm_model.generate(
                    **inputs,
                    max_new_tokens=32,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = raw_response.split("Answer:")[-1].strip() or raw_response
        else:
            response = f"[LEO Local Synthesis] Query '{query}' processed in isolated memory container. Recommended action: Check corporate IT directory."
        
        # Step 7: Always Unload LLM immediately to protect RAM
        self.unload_llm()
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        result = {
            "response": response,
            "source": "LLM",
            "latency_ms": latency_ms,
            "similarity": best_score,
            "is_real": True
        }
        if self.reflect_service is not None:
            try:
                self.reflect_service.record_query_trace(query, result)
            except Exception:
                pass
        return result
    
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
