import os
import tempfile
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.source import SourceType, SourceStatus
from app.schemas.source import SourceResponse, SourceStatusResponse, SourceType as SourceTypeEnum
from app.services import source_service
from app.config import settings

router = APIRouter(prefix="/notebooks/{notebook_id}/sources", tags=["sources"])


@router.get("", response_model=list[SourceResponse])
async def list_sources(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sources in a notebook."""
    sources = await source_service.list_sources(db, notebook_id)
    return [
        SourceResponse(
            id=s.id,
            name=s.name,
            source_type=SourceType(s.source_type.value),
            status=SourceStatus(s.status.value),
            chunk_count=s.chunk_count,
            error_message=s.error_message,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in sources
    ]


@router.post("", response_model=SourceResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_source(
    notebook_id: UUID,
    source_type: SourceType = Form(...),
    file: UploadFile | None = File(None),
    url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import a new source (URL or file upload)."""
    if source_type == SourceType.URL:
        if not url:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="URL is required for URL sources")
        name = url
    elif file:
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
        name = file.filename or "uploaded_file"

        # Save temp file for parsing
        suffix = f".{source_type.value}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is required for text/md/docx sources")

    source = await source_service.create_source(db, notebook_id, name, SourceType(source_type.value))

    # Dispatch background indexing task
    from app.workers.indexing_tasks import index_source_task
    index_source_task.delay(str(source.id), source_type.value, url=url, file_path=tmp_path if file else None)

    return SourceResponse(
        id=source.id,
        name=source.name,
        source_type=SourceType(source.source_type.value),
        status=SourceStatus(source.status.value),
        chunk_count=source.chunk_count,
        created_at=source.created_at,
        updated_at=source.updated_at
    )


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    notebook_id: UUID,
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a source."""
    deleted = await source_service.delete_source(db, source_id, notebook_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")


@router.get("/{source_id}/status", response_model=SourceStatusResponse)
async def get_source_status(
    notebook_id: UUID,
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Poll indexing status of a source."""
    status_resp = await source_service.get_source_status(db, source_id)
    if not status_resp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return status_resp
