from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Force CPU to comply with GPU-Irrelevance requirement
        self.device = 'cpu'
        self.model = SentenceTransformer(model_name, device=self.device)

    def get_embeddings(self, text_list):
        if isinstance(text_list, str):
            text_list = [text_list]
        embeddings = self.model.encode(text_list, convert_to_tensor=True)
        return embeddings.cpu().numpy()

if __name__ == "__main__":
    embedder = Embedder()
    test_text = "HYPER: Distributed Compute Protocol"
    emb = embedder.get_embeddings(test_text)
    print(f"Embedding shape: {emb.shape}")
