from sentence_transformers import SentenceTransformer

from app.config import settings


_model = None


def get_embedder():
    """Get or create the SentenceTransformer model singleton."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    embedder = get_embedder()
    embeddings = embedder.encode(texts, batch_size=batch_size, show_progress_bar=False)
    return embeddings.tolist()
