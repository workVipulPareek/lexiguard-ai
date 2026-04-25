from collections import deque

MAX_HISTORY = 5

class MemoryStore:
    def __init__(self):
        self.history = deque(maxlen=MAX_HISTORY)

    def add(self, question: str, result: dict):
        self.history.append({
            "question": question,
            "answer": result.get("answer", ""),
            "risk_score": result.get("risk_score", ""),
            "clause_types": result.get("clause_types", [])
        })

    def get_history(self) -> list:
        return list(self.history)

    def get_context_summary(self) -> str:
        if not self.history:
            return ""
        lines = []
        for i, entry in enumerate(self.history, 1):
            lines.append(f"[{i}] Q: {entry['question']} | Risk: {entry['risk_score']}")
        return "\n".join(lines)

    def clear(self):
        self.history.clear()


_store = None

def get_memory_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store