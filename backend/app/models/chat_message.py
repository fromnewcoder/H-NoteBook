import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole, name='message_role', native_enum=False), nullable=False)
    content = Column(Text, nullable=False)
    source_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    notebook = relationship("Notebook", back_populates="chat_messages")
