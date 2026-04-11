from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source, SourceType, SourceStatus
from app.schemas.source import SourceCreateURL, SourceStatusResponse
from app.utils.chroma_client import get_or_create_collection


async def list_sources(db: AsyncSession, notebook_id: UUID) -> list[Source]:
    """List all sources for a notebook."""
    result = await db.execute(
        select(Source)
        .where(Source.notebook_id == notebook_id)
        .order_by(Source.created_at.desc())
    )
    return list(result.scalars().all())


async def create_source(db: AsyncSession, notebook_id: UUID, name: str, source_type: SourceType) -> Source:
    """Create a new source with processing status."""
    source = Source(
        notebook_id=notebook_id,
        name=name,
        source_type=source_type,
        status=SourceStatus.PROCESSING
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


async def get_source(db: AsyncSession, source_id: UUID, notebook_id: UUID) -> Source | None:
    """Get a source by ID."""
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.notebook_id == notebook_id
        )
    )
    return result.scalar_one_or_none()


async def update_source_status(
    db: AsyncSession,
    source_id: UUID,
    status: SourceStatus,
    raw_content: str | None = None,
    chunk_count: int = 0,
    error_message: str | None = None,
    summary: str | None = None
) -> Source | None:
    """Update source status after processing."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        return None

    source.status = status
    if raw_content is not None:
        source.raw_content = raw_content
    if chunk_count is not None:
        source.chunk_count = chunk_count
    if error_message is not None:
        source.error_message = error_message
    if summary is not None:
        source.summary = summary

    await db.commit()
    await db.refresh(source)
    return source


async def delete_source(db: AsyncSession, source_id: UUID, notebook_id: UUID) -> bool:
    """Delete a source from ChromaDB and database."""
    source = await get_source(db, source_id, notebook_id)
    if not source:
        return False

    # Delete from ChromaDB
    collection = get_or_create_collection(str(notebook_id))
    try:
        collection.delete(where={"source_id": str(source_id)})
    except Exception:
        pass

    await db.delete(source)
    await db.commit()
    return True


async def get_source_status(db: AsyncSession, source_id: UUID) -> SourceStatusResponse | None:
    """Get source status for polling."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        return None
    return SourceStatusResponse(
        status=source.status,
        chunk_count=source.chunk_count,
        error_message=source.error_message,
        summary=source.summary
    )
