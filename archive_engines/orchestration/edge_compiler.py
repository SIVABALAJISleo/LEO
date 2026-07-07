import json
import os
import hashlib
from typing import List, Dict, Any
from .bpe_tokenizer import BPETokenizer
from .bloom_filter import SemanticBloomFilter

class EdgeCompiler:
    """
    Module C: OFFLINE SEMANTIC COMPILER
    - Generates immutable CDN endpoints from domain knowledge.
    - Compiles vocabulary, filter, and anchors.
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.tokenizer = BPETokenizer()
        self.bloom_filter = SemanticBloomFilter(size=1024 * 8)
        self.anchors: Dict[str, Dict[str, Any]] = {}

    def compile(self, knowledge_base: List[Dict[str, Any]], vocab: Dict[str, int], synonyms: Dict[str, str]):
        # 1. Initialize Tokenizer with synonym mapping
        self.tokenizer.set_vocab(vocab, {})
        # Map synonym strings to canonical token IDs
        for word, canonical_word in synonyms.items():
            if word in vocab and canonical_word in vocab:
                self.tokenizer.canonical_map[vocab[word]] = vocab[canonical_word]

        # 2. Process Knowledge Base into Anchors
        for entry in knowledge_base:
            intent = entry["intent"]
            response = entry["response"]
            wasm_module = entry.get("wasm_logic", None)

            # Tokenize + Collapse
            raw_ids = self.tokenizer.tokenize(intent)
            canonical_ids = self.tokenizer.collapse_synonyms(raw_ids)
            
            # Generate deterministic path (Hash of canonical ID sequence)
            # Use stable sorting or just order to ensure identity
            canonical_ids.sort()
            key_blob = ",".join(map(str, canonical_ids))
            anchor_hash = hashlib.sha256(key_blob.encode()).hexdigest()
            print(f"[COMPILER] Path: {intent} -> Tokens: {canonical_ids} -> Key: {key_blob} -> Hash: {anchor_hash}")
            
            # Record in Bloom Filter
            self.bloom_filter.add(anchor_hash)
            
            # Store in anchors map
            self._add_anchor(anchor_hash, response, wasm_module, "EXACT")

            # 2b. Mip-Map Backoff Generation (Precompute high-value subsets)
            # Strategy: Generate subsets by dropping 1-2 least significant tokens
            # For this demo, we'll just generate one "mip" by dropping the middle token
            if len(canonical_ids) > 2:
                mip_ids = canonical_ids.copy()
                mip_ids.pop(len(mip_ids) // 2)
                mip_ids.sort()
                mip_key = ",".join(map(str, mip_ids))
                mip_hash = hashlib.sha256(mip_key.encode()).hexdigest()
                self._add_anchor(mip_hash, response, wasm_module, "MIP_MAP")

        # 3. Export to Filesystem
        self._export()

    def _add_anchor(self, h, response, wasm, type_str):
        self.bloom_filter.add(h)
        self.anchors[h] = {
            "intent_id": h,
            "data": response,
            "wasm_ref": wasm,
            "type": type_str,
            "version": "1.0.0_immutable"
        }

    def _export(self):
        # Create CDN directories
        data_path = os.path.join(self.output_dir, "data")
        os.makedirs(data_path, exist_ok=True)

        # Export anchors
        for h, content in self.anchors.items():
            with open(os.path.join(data_path, f"{h}.json"), "w") as f:
                json.dump(content, f, indent=4)

        # Export Bloom Filter and Vocab
        manifest = {
            "bloom_filter": self.bloom_filter.export_state(),
            "vocab": self.tokenizer.vocab,
            "canonical_map": self.tokenizer.canonical_map,
            "backoff_weights": {k: 1.0 for k in self.tokenizer.vocab.values()} # Initial equal weight
        }
        with open(os.path.join(self.output_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=4)

        print(f"Compilation Complete: {len(self.anchors)} anchors exported to {self.output_dir}")
