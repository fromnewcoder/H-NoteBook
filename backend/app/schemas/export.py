from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    PDF = "pdf"
    MIND_MAP = "mind_map"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ExportCreate(BaseModel):
    format: ExportFormat


class ExportJobResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    format: ExportFormat
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
