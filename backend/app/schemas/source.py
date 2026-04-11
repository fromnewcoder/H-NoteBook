from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class SourceType(str, Enum):
    URL = "url"
    TXT = "txt"
    MD = "md"
    DOCX = "docx"


class SourceStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class SourceCreateURL(BaseModel):
    source_type: SourceType = SourceType.URL
    url: str


class SourceResponse(BaseModel):
    id: UUID
    name: str
    source_type: SourceType
    status: SourceStatus
    chunk_count: int = 0
    error_message: str | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    status: SourceStatus
    chunk_count: int = 0
    error_message: str | None = None
    summary: str | None = None
