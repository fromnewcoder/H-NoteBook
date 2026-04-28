import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services import chat_service, rag_service, source_service
from app.services.chat_service import stream_chat_response
from app.evaluations.chat import evaluate_chat_message

router = APIRouter(prefix="/notebooks/{notebook_id}/messages", tags=["chat"])


@router.get("", response_model=list[ChatMessageResponse])
async def get_messages(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full chat history for a notebook."""
    messages = await chat_service.get_messages(db, notebook_id)
    return [
        ChatMessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            source_ids=m.source_ids or [],
            created_at=m.created_at
        )
        for m in messages
    ]


@router.post("")
async def send_message(
    notebook_id: UUID,
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and stream the response via SSE."""
    # Check if all sources are ready
    if request.selected_source_ids:
        sources_ready = await rag_service.check_sources_ready(db, notebook_id, request.selected_source_ids)
        if not sources_ready:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more sources are still processing"
            )

    # Create user message
    from app.schemas.chat import ChatMessageCreate
    from app.models.chat_message import MessageRole

    user_msg = await chat_service.create_message(
        db,
        notebook_id,
        ChatMessageCreate(
            role=MessageRole.user,
            content=request.content,
            source_ids=request.selected_source_ids
        )
    )

    # Stream response
    async def event_generator():
        message_id = str(user_msg.id)
        full_response = ""

        try:
            async for token in stream_chat_response(
                notebook_id,
                request.content,
                request.selected_source_ids,
                user_id=str(current_user.id)
            ):
                if token.get("type") == "token":
                    content = token.get("content", "")
                    full_response += content
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                elif token.get("type") == "done":
                    # Persist assistant message
                    assistant_msg = await chat_service.create_message(
                        db,
                        notebook_id,
                        ChatMessageCreate(
                            role=MessageRole.assistant,
                            content=full_response,
                            source_ids=request.selected_source_ids
                        )
                    )
                    yield f"data: {json.dumps({'type': 'done', 'message_id': str(assistant_msg.id)})}\n\n"
                    # Fire-and-forget LLM-as-a-judge evaluation
                    asyncio.create_task(
                        evaluate_chat_message(str(assistant_msg.id), str(notebook_id))
                    )
                elif token.get("type") == "error":
                    yield f"data: {json.dumps({'type': 'error', 'content': token.get('content')})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
