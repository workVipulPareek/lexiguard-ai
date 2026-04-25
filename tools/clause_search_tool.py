from rag.retriever import retrieve

def clause_search_tool(question: str, file_path: str, top_k: int = 3) -> dict:
    chunks = retrieve(question, file_path, top_k=top_k)

    if not chunks:
        return {
            "found": False,
            "chunks": [],
            "message": "No relevant clauses found."
        }

    return {
        "found": True,
        "chunks": chunks,
        "message": f"{len(chunks)} relevant clause(s) retrieved."
    }