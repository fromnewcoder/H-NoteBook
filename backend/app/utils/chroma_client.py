import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


def get_chroma_client():
    """Get ChromaDB client with persistent storage."""
    return chromadb.PersistentClient(
        path=settings.chroma_persist_path,
        settings=ChromaSettings(anonymized_telemetry=False)
    )


def get_collection_name(notebook_id: str) -> str:
    """Generate collection name for a notebook."""
    return f"notebook_{notebook_id.replace('-', '_')}"


def get_or_create_collection(notebook_id: str):
    """Get or create a collection for a notebook."""
    client = get_chroma_client()
    collection_name = get_collection_name(notebook_id)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"notebook_id": str(notebook_id)}
    )


def delete_collection(notebook_id: str):
    """Delete a notebook's collection."""
    client = get_chroma_client()
    collection_name = get_collection_name(notebook_id)
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
