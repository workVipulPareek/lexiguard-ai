def load_and_chunk(file_path: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap

    return [c for c in chunks if c]