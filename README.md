# H-NoteBook

AI-Powered Web Notebook Application for RAG-based Q&A with your documents.

## Overview

H-NoteBook is a full-stack web application that allows users to create notebooks, import various document sources (URLs, TXT, Markdown, DOCX), and chat with their content using AI-powered RAG (Retrieval Augmented Generation).

## Features

- **Notebook Management**: Create, edit, and delete notebooks
- **Source Import**: Support for URLs, TXT, Markdown, and DOCX files
- **AI Chat**: Chat with your sources using MiniMax 2.7 API with RAG
- **Export**: Generate Summary PDF, Mind Map, Word, PowerPoint, and Excel exports
- **Persistent Storage**: PostgreSQL for relational data, ChromaDB for vector embeddings
- **JWT Authentication**: Secure token-based auth with Redis blocklist
- **Observability**: Langfuse tracing for all LLM calls with debugging and LLM-as-a-judge evaluations

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS, Zustand, React Router |
| Backend | Python 3.14, FastAPI, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16, ChromaDB (vector store) |
| Task Queue | Celery + Redis |
| AI | MiniMax 2.7 API (Anthropic-compatible), Sentence Transformers |
| Observability | Langfuse (tracing, debugging, LLM-as-a-judge evaluations) |

## Project Structure

```
h-notebook/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app factory
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   ├── dependencies.py   # Auth dependencies
│   │   ├── tracing.py        # Langfuse client singleton
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API route handlers
│   │   ├── services/         # Business logic
│   │   ├── workers/          # Celery tasks
│   │   ├── utils/            # Parsers, chunker, embedder
│   │   └── evaluations/      # LLM-as-a-judge evaluation triggers
│   ├── alembic/              # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios API clients
│   │   ├── store/            # Zustand stores
│   │   ├── pages/            # React page components
│   │   └── components/       # Reusable UI components
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- MiniMax API key (or Anthropic API-compatible endpoint)

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
DATABASE_URL=postgresql+asyncpg://hnb:secret@localhost:5432/hnb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
MINIMAX_API_KEY=your-api-key
MINIMAX_API_BASE_URL=https://api.minimaxi.com/anthropic
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- `db` - PostgreSQL 14.22-trixie
- `redis` - Redis 7
- `chroma` - ChromaDB
- `backend` - FastAPI on port 8000
- `worker` - Celery worker
- `frontend` - Vite dev server on port 5173

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access the Application

Open http://localhost:5173 in your browser.

**Default credentials**: `admin` / `changeme123`

## API Endpoints

Base URL: `/api/v1`

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Login and get JWT |
| POST | `/auth/logout` | Logout (blocklist token) |

### Notebooks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notebooks` | List all notebooks |
| POST | `/notebooks` | Create notebook |
| GET | `/notebooks/{id}` | Get notebook details |
| PATCH | `/notebooks/{id}` | Update title |
| DELETE | `/notebooks/{id}` | Delete notebook |

### Sources

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notebooks/{id}/sources` | List sources |
| POST | `/notebooks/{id}/sources` | Import source (URL/file) |
| DELETE | `/notebooks/{id}/sources/{src_id}` | Remove source |
| GET | `/notebooks/{id}/sources/{src_id}/status` | Poll indexing status |

### Chat

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notebooks/{id}/messages` | Get chat history |
| POST | `/notebooks/{id}/messages` | Send message (SSE stream) |

### Exports

| Method | Path | Description |
|--------|------|-------------|
| POST | `/notebooks/{id}/exports` | Enqueue export job |
| GET | `/notebooks/{id}/exports/{job_id}` | Poll export status |
| GET | `/notebooks/{id}/exports/{job_id}/download` | Download file |

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## License

MIT
