import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class SourceType(str, enum.Enum):
    URL = "url"
    TXT = "txt"
    MD = "md"
    DOCX = "docx"


class SourceStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(Enum(SourceType, name='source_type', values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    name = Column(String(512), nullable=False)
    raw_content = Column(Text)
    summary = Column(Text)
    status = Column(Enum(SourceStatus, name='source_status', values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=SourceStatus.PROCESSING)
    error_message = Column(Text)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    notebook = relationship("Notebook", back_populates="sources")
