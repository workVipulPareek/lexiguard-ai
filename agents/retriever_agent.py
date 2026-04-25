from rag.retriever import retrieve

def retriever_agent(state: dict) -> dict:
    question = state["question"]
    file_path = state["file_path"]
    chunks = retrieve(question, file_path, top_k=3)
    state["retrieved_chunks"] = chunks
    state["context"] = "\n\n".join(chunks)
    return state