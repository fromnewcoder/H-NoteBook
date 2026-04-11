from app.config import settings


def chunk_text(text: str) -> list[str]:
    """Split text into chunks using recursive separator-based splitting."""
    separators = ["\n\n", "\n", ". ", " ", ""]
    return _split_text(text, separators, settings.rag_chunk_size, settings.rag_chunk_overlap)


def _split_text(text: str, separators: list[str], chunk_size: int, overlap: int) -> list[str]:
    """Recursively split text by separators, keeping chunks within chunk_size."""
    if not text:
        return []

    # Try each separator in order
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            chunks = []
            current = ""

            for part in parts:
                candidate = current + sep + part if current else part
                if len(candidate) > chunk_size and current:
                    # Current chunk is full, save it and start new with overlap
                    chunks.append(current)
                    current = current[-overlap:] + sep + part if overlap > 0 and len(current) > overlap else part
                else:
                    current = candidate

            if current:
                chunks.append(current)

            # If chunks are still too large, recurse with shorter separators
            if any(len(c) > chunk_size for c in chunks):
                sub_chunks = []
                for chunk in chunks:
                    if len(chunk) > chunk_size:
                        sub_chunks.extend(_split_text(chunk, separators[1:], chunk_size, overlap))
                    else:
                        sub_chunks.append(chunk)
                return sub_chunks

            return [c for c in chunks if c.strip()]

    # No separator matched, return as single chunk (truncate if needed)
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    return [text[:chunk_size]]
