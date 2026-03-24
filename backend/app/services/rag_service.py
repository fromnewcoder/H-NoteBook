from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chat_message import ChatMessage, MessageRole
from app.models.source import Source, SourceStatus
from app.utils.chroma_client import get_or_create_collection
from app.utils.embedder import embed_texts


SYSTEM_PROMPT = """You are a helpful assistant for the H-NoteBook application.
You MUST answer questions exclusively based on the SOURCE DOCUMENTS provided below.
If the answer cannot be found in the source documents, respond with:
"I could not find an answer to that in your selected sources."
Do not speculate or use outside knowledge."""


async def retrieve_relevant_chunks(
    notebook_id: UUID,
    query: str,
    source_ids: list[UUID]
) -> list[dict]:
    """Query ChromaDB for relevant chunks from selected sources."""
    if not source_ids:
        return []

    collection = get_or_create_collection(str(notebook_id))

    # Embed the query
    query_embedding = embed_texts([query])[0]

    # Query ChromaDB
    where_filter = {"source_id": {"$in": [str(sid) for sid in source_ids]}}
    print(f"[DEBUG] ChromaDB query: notebook={notebook_id}, source_ids={[str(s) for s in source_ids]}, filter={where_filter}")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.rag_top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    print(f"[DEBUG] ChromaDB raw results: {results}")

    chunks = []
    if results and results.get("documents") and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "content": doc,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0
            })

    print(f"[DEBUG] ChromaDB chunks: {len(chunks)}")
    return chunks


async def get_chat_history(db: AsyncSession, notebook_id: UUID) -> list[ChatMessage]:
    """Get recent chat history for context."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.notebook_id == notebook_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(settings.rag_history_turns * 2)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))


def build_prompt(query: str, chunks: list[dict], history: list[ChatMessage]) -> str:
    """Build the full prompt with sources and history."""
    # Build source documents section
    source_docs = []
    for i, chunk in enumerate(chunks, 1):
        source_name = chunk["metadata"].get("source_name", "Unknown")
        content = chunk["content"]
        source_docs.append(f"--- Source {i}: {source_name} ---\n{content}")

    source_section = "\n\n".join(source_docs) if source_docs else "No sources provided."

    # Build conversation history
    history_lines = []
    for msg in history:
        role = "User" if msg.role == MessageRole.user else "Assistant"
        history_lines.append(f"{role}: {msg.content}")

    history_section = "\n".join(history_lines) if history_lines else "No previous messages."

    prompt = f"""{SYSTEM_PROMPT}

SOURCE DOCUMENTS:
{source_section}

CONVERSATION HISTORY:
{history_section}

USER:
{query}"""

    return prompt


async def check_sources_ready(db: AsyncSession, notebook_id: UUID, source_ids: list[UUID]) -> bool:
    """Check if all sources are ready for chat."""
    if not source_ids:
        return True

    result = await db.execute(
        select(Source).where(
            Source.id.in_(source_ids),
            Source.notebook_id == notebook_id
        )
    )
    sources = list(result.scalars().all())

    if len(sources) != len(source_ids):
        return False

    return all(s.status == SourceStatus.READY for s in sources)
