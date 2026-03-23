from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notebook import Notebook
from app.models.source import Source
from app.schemas.notebook import NotebookCreate, NotebookUpdate
from app.utils.chroma_client import delete_collection


async def list_notebooks(db: AsyncSession, user_id: UUID) -> list[Notebook]:
    """List all notebooks for a user with source counts."""
    result = await db.execute(
        select(Notebook, func.count(Source.id).label("source_count"))
        .outerjoin(Source)
        .where(Notebook.user_id == user_id)
        .group_by(Notebook.id)
        .order_by(Notebook.updated_at.desc())
    )
    return result.all()


async def create_notebook(db: AsyncSession, user_id: UUID, data: NotebookCreate) -> Notebook:
    """Create a new notebook."""
    notebook = Notebook(user_id=user_id, title=data.title)
    db.add(notebook)
    await db.commit()
    await db.refresh(notebook)
    return notebook


async def get_notebook(db: AsyncSession, notebook_id: UUID, user_id: UUID) -> Notebook | None:
    """Get a notebook by ID for a specific user."""
    result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_notebook(db: AsyncSession, notebook_id: UUID, user_id: UUID, data: NotebookUpdate) -> Notebook | None:
    """Update notebook title."""
    notebook = await get_notebook(db, notebook_id, user_id)
    if not notebook:
        return None
    notebook.title = data.title
    await db.commit()
    await db.refresh(notebook)
    return notebook


async def delete_notebook(db: AsyncSession, notebook_id: UUID, user_id: UUID) -> bool:
    """Delete a notebook and its ChromaDB collection."""
    notebook = await get_notebook(db, notebook_id, user_id)
    if not notebook:
        return False

    # Delete ChromaDB collection
    delete_collection(str(notebook_id))

    await db.delete(notebook)
    await db.commit()
    return True
