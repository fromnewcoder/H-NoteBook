from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotebookBase(BaseModel):
    title: str = "Untitled Notebook"


class NotebookCreate(NotebookBase):
    pass


class NotebookUpdate(BaseModel):
    title: str


class NotebookResponse(BaseModel):
    id: UUID
    title: str
    source_count: int = 0
    updated_at: datetime

    class Config:
        from_attributes = True


class NotebookDetailResponse(BaseModel):
    id: UUID
    title: str
    source_count: int
    updated_at: datetime

    class Config:
        from_attributes = True
