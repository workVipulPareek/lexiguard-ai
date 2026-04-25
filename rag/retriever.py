from rag.chunking import load_and_chunk
from rag.embeddings import embed_texts, embed_query
from rag.vector_store import VectorStore

_store = None

def build_index(file_path: str) -> VectorStore:
    global _store
    chunks = load_and_chunk(file_path)
    embeddings = embed_texts(chunks)
    _store = VectorStore(dimension=384)
    _store.add(chunks, embeddings)
    return _store

def retrieve(query: str, file_path: str, top_k: int = 3) -> list[str]:
    global _store
    if _store is None:
        build_index(file_path)
    query_vec = embed_query(query)
    return _store.search(query_vec, top_k=top_k)