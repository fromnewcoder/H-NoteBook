from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessageRequest(BaseModel):
    content: str
    selected_source_ids: list[UUID] = []


class ChatMessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    source_ids: list[UUID] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    role: MessageRole
    content: str
    source_ids: list[UUID] = []
