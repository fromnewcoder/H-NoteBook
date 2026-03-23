from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.notebook import Notebook
from app.schemas.notebook import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
    NotebookDetailResponse
)
from app.services import notebook_service

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


def notebook_to_response(notebook: Notebook, source_count: int = 0) -> NotebookResponse:
    """Convert notebook model to response with source count."""
    return NotebookResponse(
        id=notebook.id,
        title=notebook.title,
        source_count=source_count,
        updated_at=notebook.updated_at
    )


@router.get("", response_model=list[NotebookResponse])
async def list_notebooks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all notebooks for the authenticated user."""
    results = await notebook_service.list_notebooks(db, current_user.id)
    return [
        NotebookResponse(
            id=nb.Notebook.id,
            title=nb.Notebook.title,
            source_count=nb.source_count,
            updated_at=nb.Notebook.updated_at
        )
        for nb in results
    ]


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    data: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notebook."""
    notebook = await notebook_service.create_notebook(db, current_user.id, data)
    return NotebookResponse(
        id=notebook.id,
        title=notebook.title,
        source_count=0,
        updated_at=notebook.updated_at
    )


@router.get("/{notebook_id}", response_model=NotebookDetailResponse)
async def get_notebook(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notebook details with source list."""
    notebook = await notebook_service.get_notebook(db, notebook_id, current_user.id)
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    from sqlalchemy import func, select
    from app.models.source import Source

    result = await db.execute(
        select(func.count(Source.id)).where(Source.notebook_id == notebook_id)
    )
    source_count = result.scalar() or 0

    return NotebookDetailResponse(
        id=notebook.id,
        title=notebook.title,
        source_count=source_count,
        updated_at=notebook.updated_at
    )


@router.patch("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: UUID,
    data: NotebookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notebook title."""
    notebook = await notebook_service.update_notebook(db, notebook_id, current_user.id, data)
    if not notebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    from sqlalchemy import func, select
    from app.models.source import Source

    result = await db.execute(
        select(func.count(Source.id)).where(Source.notebook_id == notebook_id)
    )
    source_count = result.scalar() or 0

    return NotebookResponse(
        id=notebook.id,
        title=notebook.title,
        source_count=source_count,
        updated_at=notebook.updated_at
    )


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notebook and all its data."""
    deleted = await notebook_service.delete_notebook(db, notebook_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")
