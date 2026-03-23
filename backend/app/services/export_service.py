import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export_job import ExportJob, ExportFormat, JobStatus
from app.models.source import Source, SourceStatus
from app.schemas.export import ExportCreate


async def create_export_job(db: AsyncSession, notebook_id: UUID, data: ExportCreate) -> ExportJob:
    """Create a new export job."""
    job = ExportJob(
        notebook_id=notebook_id,
        format=data.format,
        status=JobStatus.QUEUED
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_export_job(db: AsyncSession, job_id: UUID) -> ExportJob | None:
    """Get an export job by ID."""
    result = await db.execute(select(ExportJob).where(ExportJob.id == job_id))
    return result.scalar_one_or_none()


async def update_export_job_status(
    db: AsyncSession,
    job_id: UUID,
    status: JobStatus,
    file_path: str | None = None,
    error_message: str | None = None
) -> ExportJob | None:
    """Update export job status."""
    job = await get_export_job(db, job_id)
    if not job:
        return None

    job.status = status
    if file_path:
        job.file_path = file_path
    if error_message:
        job.error_message = error_message
    if status in (JobStatus.DONE, JobStatus.FAILED):
        from datetime import datetime
        job.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(job)
    return job


async def get_ready_sources(db: AsyncSession, notebook_id: UUID) -> list[Source]:
    """Get all ready sources for a notebook."""
    result = await db.execute(
        select(Source).where(
            Source.notebook_id == notebook_id,
            Source.status == SourceStatus.READY
        )
    )
    return list(result.scalars().all())


async def get_all_export_jobs(db: AsyncSession, notebook_id: UUID) -> list[ExportJob]:
    """Get all export jobs for a notebook."""
    result = await db.execute(
        select(ExportJob)
        .where(ExportJob.notebook_id == notebook_id)
        .order_by(ExportJob.created_at.desc())
    )
    return list(result.scalars().all())
