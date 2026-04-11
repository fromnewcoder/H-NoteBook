import asyncio
import os
from uuid import UUID

import httpx

from app.workers.celery_app import celery_app
from app.utils.parsers.url_parser import parse_url
from app.utils.parsers.txt_parser import parse_txt
from app.utils.parsers.md_parser import parse_md
from app.utils.parsers.docx_parser import parse_docx
from app.utils.chunker import chunk_text
from app.utils.embedder import embed_texts
from app.utils.chroma_client import get_or_create_collection
from app.models.source import SourceStatus
from app.config import settings

# Import database setup for tasks
from app.database import async_session_maker


# Ensure all models are imported before SQLAlchemy relationships are resolved
from app.models import user, notebook, source, chat_message, export_job  # noqa: F401

# Persistent event loop for the worker process
_loop = None


async def generate_source_summary(text: str) -> str | None:
    """Generate a concise summary of the source content using MiniMax API."""
    if not text or len(text.strip()) < 50:
        return None

    prompt = (
        "You are a helpful assistant. Please provide a concise summary of the following content "
        "in 2-3 sentences. Focus on the main topic and key points.\n\n"
        f"Content:\n{text[:8000]}"
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": settings.minimax_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {settings.minimax_api_key}",
                "Content-Type": "application/json"
            }

            response = await client.post(
                f"{settings.minimax_api_base_url}/v1/messages",
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            result = response.json()
            content = result.get("content", None)
            if content and isinstance(content, list):
                for block in content:
                    if block.get("type") == "text":
                        return block.get("text")
            return None
    except Exception:
        return None


def _get_or_create_event_loop():
    """Get or create a persistent event loop for this process."""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


@celery_app.task(bind=True)
def index_source_task(self, source_id: str, source_type: str, url: str = None, file_path: str = None):
    """Index a source document into ChromaDB."""
    async def _index():
        from sqlalchemy import select
        from app.models.source import Source

        async with async_session_maker() as db:
            # Get source from DB
            result = await db.execute(select(Source).where(Source.id == UUID(source_id)))
            source = result.scalar_one_or_none()

            if not source:
                return

            try:
                # Step 1: Parse raw text
                if source_type == "url":
                    raw_text = await parse_url(url)
                elif source_type == "txt":
                    if file_path:
                        with open(file_path, "rb") as f:
                            raw_text = parse_txt(f.read())
                    else:
                        raise ValueError("No file provided for txt source")
                elif source_type == "md":
                    if file_path:
                        with open(file_path, "r", encoding="utf-8") as f:
                            raw_text = parse_md(f.read())
                    else:
                        raise ValueError("No file provided for md source")
                elif source_type == "docx":
                    if file_path:
                        raw_text = parse_docx(file_path)
                    else:
                        raise ValueError("No file provided for docx source")
                else:
                    raise ValueError(f"Unknown source type: {source_type}")

                # Step 1.5: Generate summary
                summary = await generate_source_summary(raw_text or "")

                # Step 2: Chunk text
                chunks = chunk_text(raw_text or "")
                if not chunks:
                    raise ValueError(f"No content extracted (raw_text length: {len(raw_text) if raw_text else 0})")

                # Step 3: Embed chunks
                embeddings = embed_texts(chunks)

                # Step 4: Upsert to ChromaDB
                collection = get_or_create_collection(str(source.notebook_id))

                ids = [f"{source_id}_{i}" for i in range(len(chunks))]
                metadatas = [
                    {
                        "source_id": source_id,
                        "notebook_id": str(source.notebook_id),
                        "source_type": source_type,
                        "source_name": source.name,
                        "chunk_index": i
                    }
                    for i in range(len(chunks))
                ]

                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas
                )

                # Step 5: Update source status
                from app.services.source_service import update_source_status
                await update_source_status(
                    db,
                    UUID(source_id),
                    SourceStatus.READY,
                    raw_content=raw_text,
                    chunk_count=len(chunks),
                    summary=summary
                )

            except (Exception, OSError) as e:
                # Update with error status
                from app.services.source_service import update_source_status
                await update_source_status(
                    db,
                    UUID(source_id),
                    SourceStatus.FAILED,
                    error_message=str(e)
                )
                raise

            finally:
                # Cleanup temp file
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)

    # Use persistent event loop instead of asyncio.run()
    loop = _get_or_create_event_loop()
    loop.run_until_complete(_index())
