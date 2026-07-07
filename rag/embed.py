from sentence_transformers import SentenceTransformer
import os
import numpy as np
import hashlib

class Embedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Force CPU to comply with GPU-Irrelevance requirement
        self.device = 'cpu'
        try:
            self.model = SentenceTransformer(model_name, device=self.device, local_files_only=True)
        except Exception:
            if os.environ.get("LEO_OFFLINE") == "1" or os.environ.get("TRANSFORMERS_OFFLINE") == "1":
                self.model = None
            else:
                try:
                    self.model = SentenceTransformer(model_name, device=self.device)
                except Exception:
                    self.model = None

    def get_embeddings(self, text_list):
        if isinstance(text_list, str):
            text_list = [text_list]
        if self.model is not None:
            embeddings = self.model.encode(text_list, convert_to_tensor=True)
            # handle list or array checks
            import torch
            if isinstance(embeddings, torch.Tensor):
                return embeddings.cpu().numpy()
            return np.array(embeddings, dtype=np.float32)
        else:
            # Mock offline deterministic embedding: return array of size [len(text_list), 384]
            res = []
            for text in text_list:
                h = int(hashlib.md5(text.encode()).hexdigest(), 16)  # nosec B324
                np.random.seed(h % (2**32))
                emb = np.random.randn(384).astype(np.float32)
                emb = emb / np.linalg.norm(emb)
                res.append(emb)
            return np.array(res, dtype=np.float32)

if __name__ == "__main__":
    embedder = Embedder()
    test_text = "HYPER: Distributed Compute Protocol"
    emb = embedder.get_embeddings(test_text)
    print(f"Embedding shape: {emb.shape}")
