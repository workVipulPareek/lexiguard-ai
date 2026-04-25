import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []

    def add(self, chunks: list[str], embeddings: list[list[float]]):
        self.chunks = chunks
        vectors = np.array(embeddings, dtype="float32")
        self.index.add(vectors)

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        vector = np.array([query_embedding], dtype="float32")
        _, indices = self.index.search(vector, top_k)
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]