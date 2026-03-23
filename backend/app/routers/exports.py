import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.export import ExportCreate, ExportJobResponse, ExportFormat, JobStatus
from app.services import export_service
from app.config import settings

router = APIRouter(prefix="/notebooks/{notebook_id}/exports", tags=["exports"])


@router.post("", response_model=ExportJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_export(
    notebook_id: UUID,
    request: ExportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enqueue an export job."""
    job = await export_service.create_export_job(db, notebook_id, request)

    # Dispatch background export task
    from app.workers.export_tasks import run_export_task
    run_export_task.delay(str(job.id), str(notebook_id), request.format.value)

    return ExportJobResponse(
        job_id=job.id,
        status=JobStatus(job.status.value),
        format=ExportFormat(job.format.value),
        created_at=job.created_at
    )


@router.get("/{job_id}", response_model=ExportJobResponse)
async def get_export_status(
    notebook_id: UUID,
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Poll export job status."""
    job = await export_service.get_export_job(db, job_id)
    if not job or str(job.notebook_id) != str(notebook_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")

    return ExportJobResponse(
        job_id=job.id,
        status=JobStatus(job.status.value),
        format=ExportFormat(job.format.value),
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at
    )


@router.get("/{job_id}/download")
async def download_export(
    notebook_id: UUID,
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the exported file."""
    job = await export_service.get_export_job(db, job_id)
    if not job or str(job.notebook_id) != str(notebook_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")

    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Export not ready")

    if not job.file_path or not os.path.exists(job.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Determine media type
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "mind_map": "text/html",
    }

    ext = job.format.value
    filename = f"export_{job_id}.{ext}"

    return FileResponse(
        job.file_path,
        media_type=media_types.get(ext, "application/octet-stream"),
        filename=filename
    )
