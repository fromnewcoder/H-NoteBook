# H-NoteBook

AI-powered web notebook for RAG-based chat with imported documents.

## Tech Stack

**Frontend:** React 18, Vite, Tailwind CSS, Zustand, React Router, Axios
**Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Pydantic
**DB:** PostgreSQL (relational) + ChromaDB (vector embeddings)
**AI:** MiniMax 2.7 API, Sentence Transformers (all-MiniLM-L6-v2)
**Tasks:** Celery + Redis
**Export:** reportlab, python-pptx, openpyxl, python-docx, pyvis

## Key Architecture

- Sources parsed/chunked (512 tokens) → embedded → stored in ChromaDB per notebook
- Chat: embed query → retrieve top-k chunks → send to MiniMax with history (SSE streaming)
- Indexing and exports run as Celery background tasks

## Default Credentials

`admin` / `changeme123`

## Run

```bash
docker compose up
```

## Key Paths

- Backend: `backend/app/`
- Frontend: `frontend/src/`
- Routers: `backend/app/routers/`
- Services: `backend/app/services/`
