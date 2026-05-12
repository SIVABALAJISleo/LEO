import faiss
import numpy as np
import os
import json

class RagIndex:
    def __init__(self, dimension=384, index_path='rag_index.faiss', metadata_path='metadata.json'):
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []

        if os.path.exists(index_path):
            print(f"[RagIndex] Loading existing index from {index_path}")
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            print(f"[RagIndex] Loaded {len(self.metadata)} documents")
        else:
            print(f"[RagIndex] Creating new empty index")

    def add(self, embeddings, metadata_list):
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(metadata_list)
        self.save()

    def search(self, query_embedding, k=5):
        # Ensure correct shape (1, dim)
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    "metadata": self.metadata[idx],
                    "distance": float(distances[0][i])
                })
        return results

    def batch_search(self, query_embeddings, k=5):
        """
        Optimized search for multiple embeddings at once.
        """
        if self.index.ntotal == 0:
            return [[] for _ in query_embeddings]
            
        embs = np.array(query_embeddings).astype('float32')
        distances, indices = self.index.search(embs, k)
        
        all_results = []
        for row_idx in range(len(indices)):
            row_results = []
            for col_idx in range(len(indices[row_idx])):
                idx = indices[row_idx][col_idx]
                if idx != -1:
                    row_results.append({
                        "metadata": self.metadata[idx],
                        "distance": float(distances[row_idx][col_idx])
                    })
            all_results.append(row_results)
        return all_results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)

if __name__ == "__main__":
    idx = RagIndex()
    # Dummy data
    dummy_emb = np.random.random((1, 384)).astype('float32')
    idx.add(dummy_emb, [{"text": "Hello World"}])
    res = idx.search(dummy_emb)
    print(f"Search result: {res}")
