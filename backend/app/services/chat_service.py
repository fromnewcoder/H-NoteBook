import json
import httpx
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat_message import ChatMessage, MessageRole
from app.schemas.chat import ChatMessageCreate
from app.services import rag_service


async def create_message(db: AsyncSession, notebook_id: UUID, data: ChatMessageCreate) -> ChatMessage:
    """Create and persist a chat message."""
    message = ChatMessage(
        notebook_id=notebook_id,
        role=data.role,
        content=data.content,
        source_ids=data.source_ids
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(db: AsyncSession, notebook_id: UUID) -> list[ChatMessage]:
    """Get all chat messages for a notebook."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.notebook_id == notebook_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(result.scalars().all())


async def stream_chat_response(
    notebook_id: UUID,
    query: str,
    source_ids: list[UUID]
):
    """Generate chat response using MiniMax API with streaming."""
    # Check if sources are ready
    # (In production, this check is done before streaming starts)

    # Retrieve relevant chunks
    chunks = await rag_service.retrieve_relevant_chunks(notebook_id, query, source_ids)

    # Get chat history
    # (We need a db session here - this would be passed in production)

    prompt = rag_service.build_prompt(query, chunks, [])

    # Call MiniMax API
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "model": settings.minimax_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {settings.minimax_api_key}",
            "Content-Type": "application/json"
        }

        async with client.stream(
            "POST",
            f"{settings.minimax_api_base_url}/v1/messages",
            json=payload,
            headers=headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield {"type": "token", "content": delta.get("text", "")}
                    except json.JSONDecodeError:
                        continue

            yield {"type": "done"}
