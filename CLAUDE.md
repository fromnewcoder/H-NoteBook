# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

H-NoteBook is an AI-powered web notebook application using **React + FastAPI**. Users create notebooks, import documents (URLs, TXT, MD, DOCX), and chat with AI using **RAG (Retrieval Augmented Generation)** with ChromaDB for vector storage and MiniMax 2.7 API for completions. Export supports PDF, Mind Map, Word, PowerPoint, and Excel via Celery background workers.

## Architecture

```
Client (React SPA) ──► FastAPI Backend ──► PostgreSQL (relational)
                              │            ChromaDB (vectors)
                              │            Redis (broker/blocklist)
                              ▼
                        Celery Worker (indexing, exports)
```

**Backend stack:** FastAPI + SQLAlchemy 2.0 (async) + Alembic + Celery + Redis + ChromaDB + sentence-transformers

**Frontend stack:** React 18 + Vite + Tailwind CSS + Zustand + React Router + Axios

**API base URL:** `/api/v1`

## Common Commands

### Development (Local)

**Prerequisites:** DB, Redis, and ChromaDB are already running via Docker. Use local venv for backend.

```bash
# Backend
cd backend
uvicorn app.main:app --reload        # Start FastAPI dev server (port 8000)

# Frontend
cd frontend
npm run dev                           # Start Vite dev server (port 5173)
```

### Database Migrations

```bash
cd backend
alembic upgrade head                  # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### Docker Services

```bash
docker-compose up -d                   # Start all services
docker-compose exec backend alembic upgrade head  # Run pending migrations
```

### Key Ports

| Service | Port |
|---------|------|
| Frontend (Vite) | 5173 |
| Backend (FastAPI) | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| ChromaDB | 8001 |

### Default Credentials

User: `admin` / Password: `changeme123`

## Architecture Patterns

### RAG Pipeline
1. Source imported → Celery task parses, chunks (512 tokens), embeds (all-MiniLM-L6-v2), upserts to ChromaDB
2. Chat: query embedded → ChromaDB top-k retrieval → MiniMax API with context → SSE stream to client

### Per-Notebook ChromaDB Collections
Collection name: `notebook_{notebook_id}` (UUID hyphens replaced with underscores). Enables fast metadata filtering by `source_id`.

### JWT Auth with Redis Blocklist
Token stored in localStorage; logout adds token to Redis blocklist with TTL = remaining token lifetime.

### Export Pipeline
Celery task → fetch sources from PostgreSQL → call MiniMax API → render file (reportlab/pyvis/python-pptx/openpyxl/python-docx) → stream download.

## Key File Locations

- Backend entry: `backend/app/main.py`
- Config: `backend/app/config.py` (pydantic-settings)
- Models: `backend/app/models/` (User, Notebook, Source, ChatMessage, ExportJob)
- Services: `backend/app/services/` (business logic)
- Celery tasks: `backend/app/workers/`
- Routers: `backend/app/routers/` (auth, notebooks, sources, chat, exports)
- Frontend API clients: `frontend/src/api/`
- Zustand stores: `frontend/src/store/`

## Testing

Tests directory exists at `backend/tests/` but is currently empty. No test framework is configured in the backend `requirements.txt`.
