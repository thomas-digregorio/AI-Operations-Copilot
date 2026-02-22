def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[str]:
    text = text or ""
    if not text.strip():
        return []

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.split_text(text)
    except Exception:
        # Fallback keeps retrieval and rules flows usable when heavy NLP deps are unavailable.
        chunks: list[str] = []
        step = max(1, chunk_size - chunk_overlap)
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            if i + chunk_size >= len(text):
                break
        return chunks
