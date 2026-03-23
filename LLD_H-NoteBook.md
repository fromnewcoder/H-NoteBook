# Low Level Design Document
## H-NoteBook — AI-Powered Web Notebook Application

| Field | Detail |
|---|---|
| Document Version | 1.0 |
| Based on PRD | v1.0 (2026-03-23) |
| Author | Engineering |
| Stack | Python (FastAPI) · PostgreSQL · ChromaDB · React |

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Directory Structure](#3-directory-structure)
4. [Database Design — PostgreSQL](#4-database-design--postgresql)
5. [Vector Database Design — ChromaDB](#5-vector-database-design--chromadb)
6. [Backend API Design](#6-backend-api-design)
7. [RAG Pipeline Design](#7-rag-pipeline-design)
8. [Export Pipeline Design](#8-export-pipeline-design)
9. [Frontend Component Design](#9-frontend-component-design)
10. [Authentication Design](#10-authentication-design)
11. [Configuration & Environment](#11-configuration--environment)
12. [Error Handling Strategy](#12-error-handling-strategy)
13. [Sequence Diagrams](#13-sequence-diagrams)

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│              React SPA  ·  Tailwind CSS  ·  Axios               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST + SSE
┌────────────────────────────▼────────────────────────────────────┐
│                    BACKEND  (FastAPI / Python)                   │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Auth Layer │  │  API Routers │  │  Background Workers    │  │
│  │  (JWT)      │  │  (REST)      │  │  (Celery / asyncio)    │  │
│  └─────────────┘  └──────┬───────┘  └──────────┬─────────────┘  │
│                          │                     │                 │
│  ┌───────────────────────▼─────────────────────▼─────────────┐  │
│  │                   Service Layer                            │  │
│  │  NotebookService · SourceService · ChatService             │  │
│  │  ExportService  · RAGService    · AuthService              │  │
│  └───────┬────────────────────┬──────────────────────────────┘  │
│          │                    │                                  │
└──────────┼────────────────────┼──────────────────────────────────┘
           │                    │
┌──────────▼──────┐   ┌─────────▼────────┐   ┌────────────────────┐
│   PostgreSQL    │   │    ChromaDB       │   │  External Services │
│                 │   │  (Vector Store)   │   │                    │
│  users          │   │  Collections:     │   │  MiniMax 2.7 API   │
│  notebooks      │   │  notebook_{id}    │   │  (AI completions)  │
│  sources        │   │                   │   │                    │
│  chat_messages  │   │  Embeddings per   │   │  URL Fetcher       │
│  export_jobs    │   │  source chunk     │   │  (httpx)           │
└─────────────────┘   └───────────────────┘   └────────────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| API framework | FastAPI | Async support, auto OpenAPI docs, Pydantic validation |
| Task queue | Celery + Redis | Offload slow indexing & export jobs from request thread |
| RAG embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Fast, free, runs locally, 384-dim |
| Vector store | ChromaDB (persistent) | Simple deployment, per-notebook collections, metadata filtering |
| Session store | Redis | JWT blocklist + Celery broker |
| File parsing | `python-docx`, `markdown-it-py`, `httpx`, `chardet` | One library per source type |
| Export | `reportlab` (PDF), `python-pptx` (PPTX), `openpyxl` (XLSX), `python-docx` (DOCX), `pyvis` (mind map) | Mature, no LibreOffice dependency |

---

## 2. Technology Stack

### Backend

| Layer | Package | Version (min) |
|---|---|---|
| Web framework | `fastapi` | 0.111 |
| ASGI server | `uvicorn[standard]` | 0.29 |
| ORM | `sqlalchemy[asyncio]` | 2.0 |
| DB driver | `asyncpg` | 0.29 |
| Migrations | `alembic` | 1.13 |
| Task queue | `celery[redis]` | 5.3 |
| HTTP client | `httpx` | 0.27 |
| Vector DB | `chromadb` | 0.5 |
| Embeddings | `sentence-transformers` | 2.7 |
| Text chunking | `langchain-text-splitters` | 0.2 |
| DOCX parsing | `python-docx` | 1.1 |
| PDF export | `reportlab` | 4.1 |
| PPTX export | `python-pptx` | 0.6 |
| XLSX export | `openpyxl` | 3.1 |
| Mind map | `pyvis` | 0.3 |
| Auth / JWT | `python-jose[cryptography]` | 3.3 |
| Password hash | `passlib[bcrypt]` | 1.7 |
| Config | `pydantic-settings` | 2.2 |
| HTML extract | `beautifulsoup4` | 4.12 |

### Frontend

| Layer | Package |
|---|---|
| Framework | React 18 |
| Bundler | Vite |
| Styling | Tailwind CSS |
| HTTP | Axios |
| State | Zustand |
| Routing | React Router v6 |
| Icons | Lucide React |

### Infrastructure

| Component | Technology |
|---|---|
| Relational DB | PostgreSQL 16 |
| Vector DB | ChromaDB (persistent local / Docker) |
| Cache / Broker | Redis 7 |
| Containerisation | Docker + Docker Compose |

---

## 3. Directory Structure

```
h-notebook/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── config.py                # Settings (pydantic-settings)
│   │   ├── database.py              # SQLAlchemy async engine + session
│   │   ├── dependencies.py          # FastAPI Depends() helpers
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── notebook.py
│   │   │   ├── source.py
│   │   │   ├── chat_message.py
│   │   │   └── export_job.py
│   │   │
│   │   ├── schemas/                 # Pydantic request / response schemas
│   │   │   ├── auth.py
│   │   │   ├── notebook.py
│   │   │   ├── source.py
│   │   │   ├── chat.py
│   │   │   └── export.py
│   │   │
│   │   ├── routers/                 # FastAPI routers (one per domain)
│   │   │   ├── auth.py
│   │   │   ├── notebooks.py
│   │   │   ├── sources.py
│   │   │   ├── chat.py
│   │   │   └── exports.py
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── notebook_service.py
│   │   │   ├── source_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   └── export_service.py
│   │   │
│   │   ├── workers/                 # Celery task definitions
│   │   │   ├── celery_app.py
│   │   │   ├── indexing_tasks.py
│   │   │   └── export_tasks.py
│   │   │
│   │   └── utils/
│   │       ├── parsers/
│   │       │   ├── url_parser.py
│   │       │   ├── txt_parser.py
│   │       │   ├── md_parser.py
│   │       │   └── docx_parser.py
│   │       ├── chunker.py
│   │       ├── embedder.py
│   │       └── chroma_client.py
│   │
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/                     # Axios API client modules
│   │   │   ├── auth.js
│   │   │   ├── notebooks.js
│   │   │   ├── sources.js
│   │   │   ├── chat.js
│   │   │   └── exports.js
│   │   ├── store/                   # Zustand stores
│   │   │   ├── authStore.js
│   │   │   └── notebookStore.js
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── HomePage.jsx
│   │   │   └── NotebookPage.jsx
│   │   └── components/
│   │       ├── layout/
│   │       │   ├── AppHeader.jsx
│   │       │   └── PageShell.jsx
│   │       ├── home/
│   │       │   ├── NotebookCard.jsx
│   │       │   └── CreateNotebookCard.jsx
│   │       ├── notebook/
│   │       │   ├── SourcePanel.jsx
│   │       │   ├── SourceItem.jsx
│   │       │   ├── AddSourceModal.jsx
│   │       │   ├── ChatPanel.jsx
│   │       │   ├── ChatMessage.jsx
│   │       │   └── ExportPanel.jsx
│   │       └── shared/
│   │           ├── Spinner.jsx
│   │           └── StatusBadge.jsx
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── .env.example
```

---

## 4. Database Design — PostgreSQL

### 4.1 Entity Relationship Diagram

```
users (1) ──────< notebooks (1) ──────< sources
                        │
                        └────────< chat_messages
                        └────────< export_jobs
```

### 4.2 DDL / ORM Model Specifications

#### Table: `users`

```sql
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    VARCHAR(64) UNIQUE NOT NULL,
    hashed_pw   VARCHAR(256) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK | `gen_random_uuid()` |
| username | VARCHAR(64) | UNIQUE, NOT NULL | Login identifier |
| hashed_pw | VARCHAR(256) | NOT NULL | bcrypt hash |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

> Seed data: one hardcoded user loaded via Alembic seed migration (per PRD Q4 — no self-registration in v1.0).

---

#### Table: `notebooks`

```sql
CREATE TABLE notebooks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL DEFAULT 'Untitled Notebook',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notebooks_user_id ON notebooks(user_id);
```

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | UUID | PK | |
| user_id | UUID | FK → users, NOT NULL | Row-level isolation |
| title | VARCHAR(255) | NOT NULL | Inline-editable |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | Updated on title change or source import |

---

#### Table: `sources`

```sql
CREATE TYPE source_type AS ENUM ('url', 'txt', 'md', 'docx');
CREATE TYPE source_status AS ENUM ('processing', 'ready', 'failed');

CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id     UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
    source_type     source_type NOT NULL,
    name            VARCHAR(512) NOT NULL,          -- display name / filename / URL
    raw_content     TEXT,                           -- extracted plain text (kept for re-indexing)
    status          source_status NOT NULL DEFAULT 'processing',
    error_message   TEXT,
    chunk_count     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sources_notebook_id ON sources(notebook_id);
```

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| notebook_id | UUID | FK → notebooks |
| source_type | ENUM | url / txt / md / docx |
| name | VARCHAR(512) | URL string or filename |
| raw_content | TEXT | Extracted text; stored for potential re-embedding |
| status | ENUM | processing → ready / failed |
| error_message | TEXT | Populated on failure |
| chunk_count | INTEGER | Number of chunks embedded in Chroma |

---

#### Table: `chat_messages`

```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id     UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
    role            message_role NOT NULL,
    content         TEXT NOT NULL,
    source_ids      UUID[],                         -- selected source IDs at time of message
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_messages_notebook_id_created ON chat_messages(notebook_id, created_at);
```

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| notebook_id | UUID | FK → notebooks |
| role | ENUM | user / assistant |
| content | TEXT | Message text |
| source_ids | UUID[] | Snapshot of selected sources when query was made |
| created_at | TIMESTAMPTZ | Ordered display |

---

#### Table: `export_jobs`

```sql
CREATE TYPE export_format AS ENUM ('pdf', 'mind_map', 'docx', 'pptx', 'xlsx');
CREATE TYPE job_status AS ENUM ('queued', 'processing', 'done', 'failed');

CREATE TABLE export_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notebook_id     UUID NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
    format          export_format NOT NULL,
    status          job_status NOT NULL DEFAULT 'queued',
    file_path       VARCHAR(512),                   -- server-side path to generated file
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

---

## 5. Vector Database Design — ChromaDB

### 5.1 Collection Strategy

One ChromaDB **collection per notebook**, named `notebook_{notebook_id}` (UUID with hyphens replaced by underscores).

**Why one collection per notebook?**
- Enables fast `where` filter by `source_id` without cross-collection noise.
- Supports complete notebook deletion by dropping the collection.
- Avoids large cross-user collection scans.

### 5.2 Document Schema (per chunk)

Each chunk stored in ChromaDB has:

```python
{
    # Chroma document ID — unique per chunk
    "id": "{source_id}_{chunk_index}",

    # The text chunk (max ~512 tokens)
    "document": "<plain text of the chunk>",

    # Embedding vector (384-dim, all-MiniLM-L6-v2)
    "embedding": [...],   # computed before upsert

    # Metadata — used for filtering
    "metadata": {
        "source_id":   "<uuid>",          # FK to sources.id
        "notebook_id": "<uuid>",          # FK to notebooks.id
        "source_type": "url|txt|md|docx",
        "source_name": "<display name>",
        "chunk_index": 0                  # 0-based within source
    }
}
```

### 5.3 Query Pattern

When the user sends a chat message with a set of selected source IDs:

```python
collection.query(
    query_embeddings=[embed(user_question)],
    n_results=5,
    where={"source_id": {"$in": [str(sid) for sid in selected_source_ids]}},
    include=["documents", "metadatas", "distances"]
)
```

Top-k chunks are assembled into the LLM context window.

### 5.4 Deletion Pattern

On source removal:
```python
collection.delete(where={"source_id": str(source_id)})
```

On notebook deletion:
```python
chroma_client.delete_collection(f"notebook_{notebook_id_underscored}")
```

---

## 6. Backend API Design

Base URL: `/api/v1`

All endpoints (except `/auth/login`) require `Authorization: Bearer <JWT>`.

### 6.1 Auth

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Validate credentials, return JWT |
| POST | `/auth/logout` | Blocklist token in Redis |

**POST `/auth/login`**
```
Request:  { "username": str, "password": str }
Response: { "access_token": str, "token_type": "bearer" }
```

---

### 6.2 Notebooks

| Method | Path | Description |
|---|---|---|
| GET | `/notebooks` | List all notebooks for authenticated user |
| POST | `/notebooks` | Create new notebook |
| GET | `/notebooks/{id}` | Get notebook detail (title, source list) |
| PATCH | `/notebooks/{id}` | Update notebook title |
| DELETE | `/notebooks/{id}` | Delete notebook + sources + chroma collection |

**GET `/notebooks` Response**
```json
[
  {
    "id": "uuid",
    "title": "My Research",
    "source_count": 4,
    "updated_at": "2026-03-23T10:00:00Z"
  }
]
```

**POST `/notebooks` Request / Response**
```json
// Request
{ "title": "New Notebook" }

// Response 201
{ "id": "uuid", "title": "New Notebook", "source_count": 0, "updated_at": "..." }
```

---

### 6.3 Sources

| Method | Path | Description |
|---|---|---|
| GET | `/notebooks/{nb_id}/sources` | List sources in notebook |
| POST | `/notebooks/{nb_id}/sources` | Import a new source (multipart or JSON) |
| DELETE | `/notebooks/{nb_id}/sources/{src_id}` | Remove source |
| GET | `/notebooks/{nb_id}/sources/{src_id}/status` | Poll indexing status |

**POST `/notebooks/{nb_id}/sources`**

Two modes depending on source type:

- **URL:** `Content-Type: application/json` → `{ "source_type": "url", "url": "https://..." }`
- **File:** `Content-Type: multipart/form-data` → `source_type=txt|md|docx` + `file=<binary>`

```json
// Response 202 (Accepted — async indexing begins)
{
  "id": "uuid",
  "name": "https://example.com/article",
  "source_type": "url",
  "status": "processing"
}
```

Indexing runs as a Celery background task. Client polls `GET /sources/{id}/status` until `status` is `ready` or `failed`.

---

### 6.4 Chat

| Method | Path | Description |
|---|---|---|
| GET | `/notebooks/{nb_id}/messages` | Return full chat history |
| POST | `/notebooks/{nb_id}/messages` | Send message; stream response via SSE |

**POST `/notebooks/{nb_id}/messages`**
```json
// Request
{
  "content": "What are the main findings?",
  "selected_source_ids": ["uuid-1", "uuid-2"]
}

// Response: text/event-stream (SSE)
data: {"type": "token", "content": "The "}
data: {"type": "token", "content": "main "}
...
data: {"type": "done", "message_id": "uuid"}
```

The assistant message is persisted to `chat_messages` only after the stream completes successfully.

---

### 6.5 Exports

| Method | Path | Description |
|---|---|---|
| POST | `/notebooks/{nb_id}/exports` | Enqueue export job |
| GET | `/notebooks/{nb_id}/exports/{job_id}` | Poll job status |
| GET | `/notebooks/{nb_id}/exports/{job_id}/download` | Stream file download |

**POST `/notebooks/{nb_id}/exports`**
```json
// Request
{ "format": "pdf" }   // pdf | mind_map | docx | pptx | xlsx

// Response 202
{ "job_id": "uuid", "status": "queued" }
```

---

## 7. RAG Pipeline Design

### 7.1 Indexing Pipeline (Celery Task)

```
Source Added
     │
     ▼
[1] Parse raw text
     │  url_parser   → httpx GET → BeautifulSoup text extraction
     │  txt_parser   → read + chardet decode
     │  md_parser    → markdown-it-py → strip tags → plain text
     │  docx_parser  → python-docx → iterate paragraphs
     ▼
[2] Chunk text
     │  RecursiveCharacterTextSplitter
     │  chunk_size=512 tokens, overlap=64 tokens
     ▼
[3] Embed chunks
     │  SentenceTransformer('all-MiniLM-L6-v2')
     │  Batch size: 32
     ▼
[4] Upsert to ChromaDB
     │  collection = notebook_{notebook_id}
     │  ids, embeddings, documents, metadatas
     ▼
[5] Update PostgreSQL sources.status = 'ready'
     │  sources.chunk_count = len(chunks)
     ▼
Done — client polling detects 'ready'
```

**Error handling:** any exception in steps 1–4 sets `status = 'failed'` and writes the exception message to `error_message`. The client can trigger a retry via `DELETE` + re-POST.

### 7.2 Chat Inference Pipeline

```
User message + selected_source_ids
     │
     ▼
[1] Embed user query
     │  same SentenceTransformer model
     ▼
[2] ChromaDB query
     │  collection.query(
     │    query_embeddings=[query_vec],
     │    n_results=5,
     │    where={"source_id": {"$in": selected_source_ids}}
     │  )
     ▼
[3] Build prompt
     │  System: "Answer ONLY based on the provided sources.
     │           If the answer is not in the sources, say so."
     │  Context: top-k chunk documents joined with separator
     │  History: last N (default 10) chat_messages from DB
     │  User: current query
     ▼
[4] Call MiniMax 2.7 API (Anthropic-compatible endpoint)
     │  Server-side HTTP call (API key never exposed to client)
     │  stream=True → token-by-token SSE forwarded to browser
     ▼
[5] On stream complete → persist assistant message to DB
```

### 7.3 Prompt Template

```
SYSTEM:
You are a helpful assistant for the H-NoteBook application.
You MUST answer questions exclusively based on the SOURCE DOCUMENTS provided below.
If the answer cannot be found in the source documents, respond with:
"I could not find an answer to that in your selected sources."
Do not speculate or use outside knowledge.

SOURCE DOCUMENTS:
--- Source: {source_name} ---
{chunk_text}
[...repeat for each retrieved chunk...]

CONVERSATION HISTORY:
{last_N_messages}

USER:
{user_question}
```

---

## 8. Export Pipeline Design

Each export is a Celery task dispatched from `POST /exports`. The task:
1. Fetches all `ready` sources for the notebook from PostgreSQL.
2. Concatenates their `raw_content` fields.
3. Calls MiniMax API to generate structured content (summary, key points, tables, etc.).
4. Renders the output file using the appropriate library.
5. Saves the file to `EXPORT_STORAGE_PATH/{job_id}.{ext}`.
6. Updates `export_jobs.status = 'done'` and `file_path`.

### 8.1 Per-Format Details

| Format | Library | AI Prompt Goal | Output |
|---|---|---|---|
| PDF (Summary Report) | `reportlab` | "Generate a structured summary with title, abstract, and key findings sections." | Styled PDF |
| Mind Map | `pyvis` (HTML) | "Return JSON: `{nodes: [{id, label}], edges: [{from, to, label}]}`" | Interactive HTML file |
| Word (.docx) | `python-docx` | "Generate content with clear headings and bullet points." | .docx |
| PowerPoint (.pptx) | `python-pptx` | "Return JSON: `[{title: str, bullets: [str]}]` for up to 10 slides." | .pptx |
| Excel (.xlsx) | `openpyxl` | "Return JSON: `[{sheet: str, headers: [str], rows: [[values]]}]`" | .xlsx |

### 8.2 Export Job State Machine

```
queued ──► processing ──► done
                │
                └──────► failed
```

Client polls `GET /exports/{job_id}` every 2 seconds until `done` or `failed`, then triggers browser download from the `/download` endpoint.

---

## 9. Frontend Component Design

### 9.1 Page: `HomePage`

**State (Zustand `notebookStore`):** `notebooks[]`, `loading`, `error`

**On mount:** `GET /notebooks` → populate store.

**Render:**
```
<PageShell>
  <div class="grid grid-cols-4 gap-4">
    <CreateNotebookCard />                    ← always first
    {notebooks.map(nb => <NotebookCard />)}
  </div>
</PageShell>
```

**`CreateNotebookCard`:** Clicking calls `POST /notebooks` with default title, then navigates to `/notebooks/:id`.

**`NotebookCard`** props: `{ id, title, source_count, updated_at }`. Clicking navigates to `/notebooks/:id`.

---

### 9.2 Page: `NotebookPage`

**URL:** `/notebooks/:notebookId`

**Local state:**
```js
{
  notebook: { id, title },
  sources: Source[],
  selectedSourceIds: Set<uuid>,
  messages: Message[],
  inputText: string,
  streaming: boolean,
  addSourceModalOpen: boolean,
}
```

**Layout (CSS Grid):**
```
┌──────────────────────────────────────────────────┐
│  AppHeader (title inline-edit)                   │
├──────────┬──────────────────────────┬────────────┤
│ Source   │                          │  Export    │
│ Panel    │     Chat Panel           │  Panel     │
│ (left)   │     (centre)             │  (right)   │
└──────────┴──────────────────────────┴────────────┘
```

**`SourcePanel`**
- "Add Source" button → opens `AddSourceModal`
- Maps `sources[]` → `<SourceItem>` with checkbox for selection
- Default: all sources selected on page load
- Selecting / deselecting updates `selectedSourceIds`

**`SourceItem`** props: `{ id, source_type, name, status }`
- Shows type icon (Globe / FileText / FileCode / FileWord)
- Shows `<StatusBadge status={status} />`
- Remove button → `DELETE /sources/:id` + polling stop + Chroma delete (server-side)

**`AddSourceModal`**
- Tab select: URL | TXT | MD | DOCX
- URL mode: text input → `POST /sources { source_type: "url", url }`
- File mode: `<input type="file">` → multipart `POST /sources`
- On submit: close modal, add source to list with `status: "processing"`, start polling

**`ChatPanel`**
- Renders `messages[]` as `<ChatMessage role content />`
- If no sources: shows empty-state prompt "Add sources to start chatting"
- Bottom input: textarea + send button
- On send: `POST /messages` → open SSE stream → append tokens in real time to last message

**`ExportPanel`**
- 5 buttons (Summary PDF, Mind Map, Word, PowerPoint, Excel)
- On click: `POST /exports { format }` → receives `job_id` → polls status every 2s
- Shows spinner while `processing`; on `done` triggers `GET /exports/{job_id}/download`

---

### 9.3 Component State Flow

```
AddSourceModal
  └─[POST /sources]──► SourcePanel.sources[] (status: processing)
                            └─[poll /sources/:id/status]──► status: ready/failed

ChatPanel input
  └─[POST /messages]──► SSE stream ──► append tokens ──► persist on done

ExportPanel button
  └─[POST /exports]──► job_id ──► poll ──► download trigger
```

---

## 10. Authentication Design

### Mechanism: JWT (HS256) with Redis blocklist

| Property | Value |
|---|---|
| Algorithm | HS256 |
| Expiry | 8 hours |
| Payload | `{ sub: user_id, username, exp }` |
| Storage (client) | `localStorage` (SPA) |
| Logout | Token added to Redis blocklist with TTL = remaining token lifetime |

### Hardcoded Seed User (v1.0)

Per PRD Q4, no registration flow. One user is created via an Alembic seed migration:

```python
# alembic/versions/0002_seed_user.py
def upgrade():
    op.execute("""
        INSERT INTO users (id, username, hashed_pw)
        VALUES (
            gen_random_uuid(),
            'admin',
            '$2b$12$<bcrypt-hash-of-default-password>'
        )
        ON CONFLICT (username) DO NOTHING;
    """)
```

The plaintext password is defined only in `.env` as `SEED_USER_PASSWORD` and hashed at migration time.

### FastAPI Dependency

```python
# dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    if await redis.get(f"blocklist:{token}"):
        raise HTTPException(401, "Token revoked")
    payload = decode_jwt(token)
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(401)
    return user
```

---

## 11. Configuration & Environment

### `.env.example`

```ini
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://hnb:secret@localhost:5432/hnb

# Redis
REDIS_URL=redis://localhost:6379/0

# ChromaDB
CHROMA_PERSIST_PATH=./chroma_data

# JWT
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=8

# MiniMax API (Anthropic-compatible)
MINIMAX_API_KEY=your-key-here
MINIMAX_API_BASE_URL=https://api.minimaxi.com/anthropic
MINIMAX_MODEL=MiniMax-M2.7

# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Export file storage
EXPORT_STORAGE_PATH=./exports

# Seed user
SEED_USER_PASSWORD=changeme123

# RAG tuning
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=64
RAG_TOP_K=5
RAG_HISTORY_TURNS=10

# File upload
MAX_UPLOAD_SIZE_MB=10
```

### `config.py` (Pydantic Settings)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    chroma_persist_path: str = "./chroma_data"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8
    minimax_api_key: str
    minimax_api_base_url: str
    minimax_model: str = "MiniMax-Text-2.7"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    export_storage_path: str = "./exports"
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 64
    rag_top_k: int = 5
    rag_history_turns: int = 10
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 12. Error Handling Strategy

### HTTP Error Codes

| Scenario | HTTP Code | Detail |
|---|---|---|
| Invalid credentials | 401 | "Invalid username or password" |
| Expired / revoked token | 401 | "Token invalid or expired" |
| Resource not found | 404 | "{Resource} not found" |
| File too large | 413 | "File exceeds 10 MB limit" |
| Unsupported file type | 422 | "Unsupported source type" |
| Source still processing (chat) | 409 | "Source {id} is not yet ready" |
| Internal error | 500 | Sanitised message; full trace logged |

### Source Indexing Failures

- Parser exceptions → `source.status = 'failed'`, `error_message` stored.
- UI shows "Failed" badge with retry option (re-POST).

### Export Failures

- Task exception → `export_job.status = 'failed'`.
- Client receives failure status on next poll; user may retry.

### LLM API Failures

- `httpx.TimeoutException` → return SSE event `{"type": "error", "content": "LLM request timed out. Please try again."}`
- Non-2xx response from MiniMax → same pattern with sanitised message.
- Message is NOT persisted on failure.

---

## 13. Sequence Diagrams

### 13.1 Add Source (URL)

```
Browser          FastAPI          Celery Worker       PostgreSQL    ChromaDB
   │                │                   │                  │           │
   │─POST /sources──►                   │                  │           │
   │                │──INSERT source────►                  │           │
   │                │  (status=processing)                 │           │
   │                │──dispatch task────►                  │           │
   │◄──202 Accepted─│                   │                  │           │
   │                │                   │─httpx GET url─►  │           │
   │                │                   │─parse HTML        │           │
   │                │                   │─chunk text        │           │
   │                │                   │─embed chunks      │           │
   │                │                   │──────────────────────upsert──►│
   │                │                   │──UPDATE status=ready──────────►
   │                │                   │                  │           │
   │─GET /sources/{id}/status──►        │                  │           │
   │◄──{ status: "ready" }─────         │                  │           │
```

### 13.2 Chat Message

```
Browser          FastAPI          ChromaDB        MiniMax API    PostgreSQL
   │                │                │                 │              │
   │─POST /messages─►                │                 │              │
   │                │─embed query───►│                 │              │
   │                │◄─top-k chunks──│                 │              │
   │                │─GET history────────────────────────────────────►│
   │                │◄─last N msgs───────────────────────────────────│
   │                │─build prompt   │                 │              │
   │                │────────────────────stream req────►              │
   │◄─SSE tokens────│◄───────────────────token stream──│              │
   │  (streaming)   │                │                 │              │
   │                │────────────────────────────────────INSERT msg──►│
   │◄─SSE done──────│                │                 │              │
```

### 13.3 Export Job

```
Browser          FastAPI          Celery Worker    MiniMax API    PostgreSQL
   │                │                   │               │              │
   │─POST /exports──►                   │               │              │
   │                │──INSERT job (queued)──────────────────────────► │
   │                │──dispatch task────►               │              │
   │◄──202 {job_id}─│                   │               │              │
   │                │                   │─fetch sources─────────────► │
   │                │                   │─build prompt  │              │
   │                │                   │───────────────► AI response  │
   │                │                   │─render file                  │
   │                │                   │──UPDATE job=done──────────► │
   │─GET /exports/{job_id}──►           │               │              │
   │◄──{ status: "done" }───            │               │              │
   │─GET /exports/{job_id}/download──►  │               │              │
   │◄──file stream──────────────────────│               │              │
```

---

## 14. Docker Compose (Development)

```yaml
# docker-compose.yml
version: "3.9"
services:

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: hnb
      POSTGRES_USER: hnb
      POSTGRES_PASSWORD: secret
    ports: ["5432:5432"]
    volumes: ["pg_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [db, redis]
    volumes:
      - ./backend:/app
      - chroma_data:/app/chroma_data
      - export_data:/app/exports

  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    env_file: .env
    depends_on: [db, redis]
    volumes:
      - ./backend:/app
      - chroma_data:/app/chroma_data
      - export_data:/app/exports

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

volumes:
  pg_data:
  chroma_data:
  export_data:
```

---

## 15. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-03-23 | Engineering | Initial LLD based on PRD v1.0 |
