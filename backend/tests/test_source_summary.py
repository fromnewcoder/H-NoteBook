"""Unit tests for source summary feature."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.models.source import Source, SourceType, SourceStatus
from app.schemas.source import SourceResponse, SourceStatusResponse
from app.services.source_service import update_source_status


class TestSourceModelSummary:
    """Test that Source model has summary field."""

    def test_source_model_has_summary_column(self):
        """Verify Source model has summary attribute."""
        assert hasattr(Source, 'summary')

    def test_source_summary_defaults_to_none(self):
        """Verify summary column exists and is nullable."""
        # Check the column is nullable (no notnull constraint)
        summary_column = Source.__table__.columns['summary']
        assert summary_column.nullable is True


class TestSourceSchemasSummary:
    """Test that Pydantic schemas include summary field."""

    def test_source_response_includes_summary(self):
        """Verify SourceResponse includes summary field."""
        from datetime import datetime
        schema = SourceResponse(
            id=uuid4(),
            name="Test Source",
            source_type="url",
            status="ready",
            chunk_count=5,
            summary="This is a test summary",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert schema.summary == "This is a test summary"

    def test_source_response_summary_defaults_to_none(self):
        """Verify SourceResponse summary defaults to None."""
        from datetime import datetime
        schema = SourceResponse(
            id=uuid4(),
            name="Test Source",
            source_type="url",
            status="ready",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert schema.summary is None

    def test_source_status_response_includes_summary(self):
        """Verify SourceStatusResponse includes summary field."""
        schema = SourceStatusResponse(
            status="ready",
            chunk_count=5,
            summary="Test summary",
        )
        assert schema.summary == "Test summary"


@pytest.mark.asyncio
async def test_update_source_status_with_summary():
    """Verify update_source_status accepts and stores summary."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_source = MagicMock()
    mock_source.summary = None
    mock_source.status = SourceStatus.PROCESSING
    mock_result.scalar_one_or_none.return_value = mock_source
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    await update_source_status(
        db=mock_session,
        source_id=uuid4(),
        status=SourceStatus.READY,
        summary="Generated summary text"
    )

    assert mock_source.summary == "Generated summary text"
    mock_session.commit.assert_called_once()


class TestIndexingTaskSummary:
    """Test summary generation in indexing pipeline."""

    @pytest.mark.asyncio
    async def test_generate_summary_called_after_parse(self):
        """Verify summary is generated after parsing raw text."""
        from app.workers.indexing_tasks import generate_source_summary

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"content": "This is the generated summary."}

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.__aexit__.return_value = None

            summary = await generate_source_summary("Some document content that is long enough to generate a summary from.")

            assert summary == "This is the generated summary."

    @pytest.mark.asyncio
    async def test_generate_summary_short_text_returns_none(self):
        """Verify short text returns None without calling API."""
        from app.workers.indexing_tasks import generate_source_summary

        result = await generate_source_summary("Too short")
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_empty_text_returns_none(self):
        """Verify empty text returns None without calling API."""
        from app.workers.indexing_tasks import generate_source_summary

        result = await generate_source_summary("")
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_api_failure_returns_none(self):
        """Verify API failure returns None gracefully."""
        from app.workers.indexing_tasks import generate_source_summary

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=Exception("API Error"))
            mock_client.return_value.__aenter__.return_value.__aexit__.return_value = None

            result = await generate_source_summary("Some document content that is long enough to generate a summary from.")

            assert result is None
