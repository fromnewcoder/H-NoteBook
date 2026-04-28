from langfuse import Langfuse

_langfuse_client = None


def get_langfuse() -> Langfuse:
    """Singleton Langfuse client, lazy-initialized per process."""
    global _langfuse_client
    if _langfuse_client is None:
        from app.config import settings

        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    return _langfuse_client