# LawyerGPT — CLAUDE.md

## 1. Project Overview

**LawyerGPT** is a RAG (Retrieval-Augmented Generation) based legal chatbot with source citations.

Lawyers, attorneys, and legal professionals can ask any legal question through a ChatGPT-style
interface and receive answers that are:
- Grounded in a curated corpus of ingested legal documents (US federal law, state statutes, internal firm documents)
- Streamed token-by-token in real time
- Backed by source citations — every response references the exact document, page number, and excerpt used to generate the answer

**Source citations are a core, non-negotiable feature of LawyerGPT.** Every assistant response
must be traceable back to its source material so legal professionals can verify, trust, and
act on the information provided.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Presentation Layer (React/TS)                   │
│  Sidebar │ Chat Area │ Citation Panel │ Upload Modal             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP / SSE (streaming)
┌──────────────────────────▼──────────────────────────────────────┐
│                  Service Layer (FastAPI / Python)                 │
│  Routes │ Services │ Models │ Schemas │ SQLite DB               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ In-process function calls
┌──────────────────────────▼──────────────────────────────────────┐
│                    AI Layer (LangChain / Python)                  │
│                                                                   │
│  ┌─────── Ingestion Pipeline ────────┐                           │
│  │ loader.py → chunker.py →          │                           │
│  │ embedder.py → vector_store_loader │                           │
│  └───────────────────────────────────┘                           │
│                                                                   │
│  ┌─────── Query Orchestration ───────┐                           │
│  │ retriever.py → augmentation.py →  │                           │
│  │ generation.py                     │                           │
│  └───────────────────────────────────┘                           │
│                                                                   │
│  ChromaDB (local, persistent)                                     │
└─────────────────────────────────────────────────────────────────┘
```

The FastAPI server and engine run as the **same Python process**. The engine
(`lawyergpt-engine`) is installed as a local editable package inside the server.

---

## 3. Layer-wise Structure

### Layer 1 — Presentation Layer (Client)

**Repo:** `lawyergpt-client`
**Tech:** React 18, TypeScript, Vite, Tailwind CSS, Zustand

**Responsibilities:**
- Render the ChatGPT-style UI (sidebar + chat area + citation panel)
- Stream and display assistant responses token-by-token via SSE
- Display source citations as expandable cards below each assistant message
- Allow users to upload PDF documents via a drag-and-drop modal
- Manage and display past conversations grouped by date
- Maintain UI state (active conversation, sidebar toggle, modal open/close)

**Key Components:**

| Component | Responsibility |
|---|---|
| `Sidebar` | Fixed left panel — conversation list, new chat, upload trigger |
| `ConversationList` | Renders past conversations grouped by Today / Yesterday / Last 7 Days |
| `NewChatButton` | Creates a new conversation via API, clears chat area |
| `ChatArea` | Main scrollable message area |
| `MessageBubble` | Renders a single user or assistant message |
| `StreamingMessage` | Appends incoming SSE tokens in real time |
| `CitationCard` | Displays one citation: source file, page number, excerpt |
| `CitationList` | Renders all citations below an assistant message |
| `UploadModal` | Drag-and-drop PDF upload modal with ingestion status per file |
| `MessageInput` | Text input bar fixed to bottom; sends message on Enter |

**State Management (Zustand):**

| Store | State held |
|---|---|
| `conversationStore` | List of conversations, active conversation ID, messages |
| `uiStore` | Sidebar open/close, upload modal open/close |

**API Communication:**
- `conversationApi.ts` — CRUD for conversations and messages
- `documentApi.ts` — PDF upload and ingestion status polling
- `useStreaming.ts` hook — consumes SSE stream, dispatches token/citation/done events

---

### Layer 2 — Service Layer (Server)

**Repo:** `lawyergpt-server`
**Tech:** Python 3.12+, FastAPI, SQLAlchemy (async), aiosqlite, pydantic-settings

**Responsibilities:**
- Expose REST + SSE APIs consumed by the client
- Persist conversations, messages, and citations in SQLite
- Accept PDF uploads, save to disk, and trigger the engine ingestion pipeline
- Bridge client requests to the engine (query orchestration)
- Handle all logging, exception mapping, and CORS

**Internal Architecture (strict separation):**

```
Request → Route → Service → Model/DB
                         ↘ AI Bridge → Engine
```

| Sub-module | Responsibility |
|---|---|
| `routes/` | Thin HTTP handlers — parse request, call service, return response |
| `services/` | All business logic — orchestrates DB + AI layer calls |
| `models/` | SQLAlchemy ORM table definitions |
| `schemas/` | Pydantic request/response validation models |
| `database/db.py` | Async SQLAlchemy engine + session factory |
| `core/config.py` | All settings loaded from `.env` via pydantic-settings |
| `core/logging.py` | Structured JSON logger |
| `core/exceptions.py` | Custom exception hierarchy |
| `middleware/error_handler.py` | Maps exceptions → sanitized HTTP error responses |
| `services/ai_bridge.py` | Calls engine query pipeline; yields SSE token stream |

**Key Routes:**

| Route | Method | Action |
|---|---|---|
| `/api/conversations` | GET, POST | List or create conversations |
| `/api/conversations/{id}` | GET, DELETE, PATCH | Get, delete, or rename conversation |
| `/api/conversations/{id}/messages` | POST (SSE) | Send message → stream response + citations |
| `/api/documents/upload` | POST | Upload PDF → trigger ingestion |
| `/api/documents` | GET | List documents with ingestion status |
| `/api/health` | GET | Health check |

---

### Layer 3 — Engine Layer (LangChain Pipelines)

**Repo:** `lawyergpt-engine`
**Tech:** Python 3.12+, LangChain, OpenAI (GPT-5.5, text-embedding-3-large), ChromaDB

**Responsibilities:**
- Ingest PDF documents into ChromaDB via an ETL pipeline
- Answer legal queries by retrieving relevant chunks and generating cited responses
- Stream generated tokens back to the service layer
- Manage the ChromaDB client as a singleton

**Pipeline 1 — Data Ingestion (ETL):**

| File | Phase | Responsibility |
|---|---|---|
| `ingestion/loader.py` | Extract | Load PDF pages using PyPDFLoader; fall back to UnstructuredPDFLoader with OCR for scanned docs |
| `ingestion/chunker.py` | Transform | Split pages into chunks (size=2000, overlap=100) using RecursiveCharacterTextSplitter |
| `ingestion/embedder.py` | Transform | Generate embeddings using text-embedding-3-large (3072-dim vectors) |
| `ingestion/vector_store_loader.py` | Load | Batch upsert chunks into ChromaDB (100 vectors/batch); stores metadata per chunk |

**Pipeline 2 — Query Orchestration:**

| File | Stage | Responsibility |
|---|---|---|
| `query/retriever.py` | Retrieve | Embed user query → similarity search in ChromaDB → return top-5 chunks with metadata |
| `query/augmentation.py` | Augment | Compose system prompt + numbered [1][2] context block + user query + conversation history |
| `query/generation.py` | Generate | Stream GPT-5.5 response → yield tokens + emit final citations array |

**Shared Core:**

| File | Responsibility |
|---|---|
| `core/vector_store.py` | ChromaDB client singleton (persistent local path) |
| `core/config.py` | Settings from `.env` (model names, batch sizes, top-k, paths) |
| `core/logging.py` | Shared structured logger |
| `core/exceptions.py` | Engine exception hierarchy |

**Inter-layer Communication:**
The engine is installed as a local editable Python package inside `lawyergpt-server`:
```
uv add --editable ../lawyergpt-engine
```
The server's `ai_bridge.py` imports engine functions directly — no HTTP, no subprocess.
Both layers share the same Python process and runtime.

---

## 4. Repository Structure

Three separate Git repositories:

| Repo | Purpose |
|---|---|
| `lawyergpt-client` | React + TypeScript UI |
| `lawyergpt-server` | FastAPI service layer + SQLite |
| `lawyergpt-engine` | LangChain ingestion & query pipelines |

`lawyergpt-engine` is installed into `lawyergpt-server` as an editable local package:
```
uv add --editable ../lawyergpt-engine
```
This means both server and engine share the same Python runtime — one deployed service.

---

## 4. Tech Stack

| Concern | Technology |
|---|---|
| UI framework | React 18 + TypeScript |
| UI build tool | Vite |
| UI state | Zustand |
| UI styling | Tailwind CSS |
| Backend framework | FastAPI |
| Backend language | Python 3.12+ |
| AI framework | LangChain |
| LLM (generation) | GPT-5.5 (OpenAI) |
| Embeddings | text-embedding-3-large (OpenAI) |
| Vector database | ChromaDB (local, persistent) |
| Relational database | SQLite (via SQLAlchemy + aiosqlite) |
| Dependency management | UV |
| Streaming protocol | Server-Sent Events (SSE) |
| PDF parsing | LangChain PyPDFLoader + Unstructured (OCR fallback) |
| Logging | Python `logging` module (structured, JSON-formatted) |

---

## 5. UI Layout Structure

The UI is inspired by ChatGPT's layout — a fixed left sidebar with conversation history
and a full-height main chat area on the right.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          LawyerGPT                                        │
├─────────────────────┬────────────────────────────────────────────────────┤
│                     │                                                      │
│   SIDEBAR           │   CHAT AREA                                          │
│   (fixed, 260px)    │   (flex, fills remaining width)                      │
│                     │                                                      │
│  ┌───────────────┐  │  ┌──────────────────────────────────────────────┐   │
│  │ + New Chat    │  │  │  MESSAGE LIST (scrollable)                    │   │
│  └───────────────┘  │  │                                               │   │
│                     │  │  ┌─────────────────────────────────────────┐  │   │
│  ┌───────────────┐  │  │  │ USER BUBBLE (right-aligned)             │  │   │
│  │ Upload Docs   │  │  │  │ "What are the penalties for..."         │  │   │
│  └───────────────┘  │  │  └─────────────────────────────────────────┘  │   │
│                     │  │                                               │   │
│  Past Conversations │  │  ┌─────────────────────────────────────────┐  │   │
│  ─────────────────  │  │  │ ASSISTANT BUBBLE (left-aligned)         │  │   │
│  › Today            │  │  │ Streamed answer text with [1][2]        │  │   │
│    Contract Review  │  │  │ citation markers inline...              │  │   │
│    NDA Analysis     │  │  └─────────────────────────────────────────┘  │   │
│                     │  │  ┌─────────────────────────────────────────┐  │   │
│  › Yesterday        │  │  │ CITATION LIST (below assistant bubble)  │  │   │
│    IP Dispute       │  │  │ [1] contract_law.pdf · Page 14          │  │   │
│    Tort Liability   │  │  │     "...relevant excerpt..."            │  │   │
│                     │  │  │ [2] us_code_title18.pdf · Page 203      │  │   │
│  › Last 7 Days      │  │  │     "...relevant excerpt..."            │  │   │
│    ...              │  │  └─────────────────────────────────────────┘  │   │
│                     │  └──────────────────────────────────────────────┘   │
│                     │                                                      │
│                     │  ┌──────────────────────────────────────────────┐   │
│                     │  │  MESSAGE INPUT BAR (fixed bottom)             │   │
│                     │  │  [ Ask a legal question...          ] [Send]  │   │
│                     │  └──────────────────────────────────────────────┘   │
└─────────────────────┴────────────────────────────────────────────────────┘
```

### Layout Zones

| Zone | Component | Behavior |
|---|---|---|
| **Sidebar** | `Sidebar.tsx` | Fixed left, 260px wide, dark background |
| **New Chat button** | `NewChatButton.tsx` | Creates new conversation, clears chat area |
| **Upload Docs button** | triggers `UploadModal.tsx` | Opens drag-and-drop PDF upload modal |
| **Conversation list** | `ConversationList.tsx` | Grouped by date (Today / Yesterday / Last 7 Days), clickable |
| **Chat area** | `ChatArea.tsx` | Fills remaining width, scrollable message list |
| **User bubble** | `MessageBubble.tsx` | Right-aligned, distinct background |
| **Assistant bubble** | `MessageBubble.tsx` + `StreamingMessage.tsx` | Left-aligned, streams tokens live |
| **Citation list** | `CitationList.tsx` + `CitationCard.tsx` | Appears below assistant bubble after stream ends, expandable cards |
| **Message input** | `MessageInput.tsx` | Fixed to bottom of chat area, multi-line support, send on Enter |

### Upload Modal (overlay)

```
┌─────────────────────────────────────────────┐
│  Upload Legal Documents                  [×] │
├─────────────────────────────────────────────┤
│                                             │
│   ┌─────────────────────────────────────┐  │
│   │                                     │  │
│   │   Drag & drop PDF files here        │  │
│   │   or click to browse                │  │
│   │                                     │  │
│   └─────────────────────────────────────┘  │
│                                             │
│   Uploaded files:                           │
│   ✓ contract_law_2024.pdf  (completed)      │
│   ⟳ us_code_title18.pdf   (processing)     │
│   ✗ old_statute.pdf        (failed)         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 6. Folder Structure — Client (`lawyergpt-client`)

```
lawyergpt-client/
├── public/
├── src/
│   ├── components/
│   │   ├── Sidebar/
│   │   │   ├── Sidebar.tsx            # Sidebar shell
│   │   │   ├── ConversationList.tsx   # Past conversations list
│   │   │   └── NewChatButton.tsx      # Start new conversation
│   │   ├── ChatArea/
│   │   │   ├── ChatArea.tsx           # Main chat container
│   │   │   ├── MessageList.tsx        # Renders all messages
│   │   │   ├── MessageBubble.tsx      # Single message (user/assistant)
│   │   │   ├── StreamingMessage.tsx   # Live token streaming display
│   │   │   └── MessageInput.tsx       # Input box + send button
│   │   ├── CitationPanel/
│   │   │   ├── CitationCard.tsx       # Single citation (source, page, excerpt)
│   │   │   └── CitationList.tsx       # List of citations below a message
│   │   └── UploadModal/
│   │       ├── UploadModal.tsx        # Modal shell
│   │       └── DropZone.tsx           # Drag-and-drop PDF zone
│   ├── hooks/
│   │   ├── useConversation.ts         # CRUD for conversations
│   │   ├── useStreaming.ts            # SSE stream consumption
│   │   └── useDocumentUpload.ts       # PDF upload state
│   ├── services/
│   │   ├── api.ts                     # Axios base client, base URL, interceptors
│   │   ├── conversationApi.ts         # Conversation + message API calls
│   │   └── documentApi.ts             # Document upload + status API calls
│   ├── store/
│   │   ├── conversationStore.ts       # Zustand: conversations, active conversation
│   │   └── uiStore.ts                 # Zustand: sidebar open/close, modal state
│   ├── types/
│   │   ├── conversation.ts
│   │   ├── message.ts
│   │   ├── citation.ts
│   │   └── document.ts
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
└── package.json
```

---

## 7. Folder Structure — Server (`lawyergpt-server`)

```
lawyergpt-server/
├── app/
│   ├── main.py                        # FastAPI app entry, middleware registration
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── conversations.py           # GET/POST/DELETE /conversations
│   │   ├── messages.py                # POST /conversations/{id}/messages (SSE)
│   │   ├── documents.py               # POST /documents/upload, GET /documents
│   │   └── health.py                  # GET /health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation_service.py    # Business logic for conversations
│   │   ├── message_service.py         # Business logic for messages + citation storage
│   │   ├── document_service.py        # Business logic for document upload + ingestion trigger
│   │   └── ai_bridge.py               # Bridge: calls engine query pipeline
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py            # SQLAlchemy ORM model
│   │   ├── message.py                 # SQLAlchemy ORM model
│   │   ├── citation.py                # SQLAlchemy ORM model
│   │   └── document.py                # SQLAlchemy ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── conversation_schema.py     # Pydantic request/response schemas
│   │   ├── message_schema.py
│   │   └── document_schema.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                      # SQLAlchemy async engine, session factory
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Settings via pydantic-settings (.env)
│   │   ├── logging.py                 # Structured JSON logger setup
│   │   └── exceptions.py             # Custom exception classes
│   └── middleware/
│       ├── __init__.py
│       ├── error_handler.py           # Global exception → HTTP error mapper
│       └── cors.py                    # CORS configuration
├── .env                               # Server-side env vars (never committed)
├── .env.example
├── pyproject.toml
└── uv.lock
```

---

## 8. Folder Structure — Engine (`lawyergpt-engine`)

```
lawyergpt-engine/
├── ingestion/
│   ├── __init__.py
│   ├── loader.py                      # Extract: PDF loading (PyPDFLoader + OCR fallback)
│   ├── chunker.py                     # Transform: RecursiveCharacterTextSplitter
│   ├── embedder.py                    # Transform: OpenAI text-embedding-3-large
│   └── vector_store_loader.py         # Load: batch upsert into ChromaDB (100/batch)
├── query/
│   ├── __init__.py
│   ├── retriever.py                   # Semantic search → top-k chunks + metadata
│   ├── augmentation.py                # Build system prompt + user query + cited context
│   └── generation.py                  # Call GPT-5.5 with streaming, return answer + citations
├── core/
│   ├── __init__.py
│   ├── config.py                      # Settings via pydantic-settings (.env)
│   ├── logging.py                     # Shared logger
│   ├── exceptions.py                 # Engine custom exceptions
│   └── vector_store.py               # ChromaDB client singleton (persistent local)
├── scripts/
│   └── ingest.py                      # CLI: run full ingestion pipeline on a directory
├── .env
├── .env.example
├── pyproject.toml
└── uv.lock
```

---

## 8. AI Pipelines

### 8.1 Data Ingestion Pipeline (ETL)

**Trigger:** User uploads a PDF via the UI → backend saves file → calls ingestion pipeline.

```
PDF File(s)
    │
    ▼
[Extract] loader.py
    • Primary: LangChain PyPDFLoader (page-level extraction)
    • Fallback: UnstructuredPDFLoader with OCR (for scanned/image PDFs)
    • Output: List[Document] with metadata {source, page, filename}
    │
    ▼
[Transform — Chunk] chunker.py
    • RecursiveCharacterTextSplitter
    • chunk_size = 2000
    • chunk_overlap = 100
    • Output: List[Document] (chunked) with inherited metadata
    │
    ▼
[Transform — Embed] embedder.py
    • Model: text-embedding-3-large (OpenAI)
    • Input: chunk text
    • Output: List[float] (3072-dim vectors) per chunk
    │
    ▼
[Load] vector_store_loader.py
    • Batch size: 100 vectors per batch
    • Upserts into local ChromaDB collection
    • Stores metadata per chunk: {source_file, page_number, chunk_id, excerpt}
    • Logs batch progress and failures
```

### 8.2 Query Orchestration Pipeline

**Trigger:** User sends a message → backend streams response via SSE.

```
User Query (string) + Conversation History
    │
    ▼
[Retrieve] retriever.py
    • Embeds user query using text-embedding-3-large
    • Similarity search in ChromaDB (top-k = 5 by default)
    • Returns: List[RetrievedChunk] with {text, source_file, page_number, chunk_id, score}
    │
    ▼
[Augment] augmentation.py
    • Constructs three-part prompt:
        1. System prompt: role definition, citation instruction, answer style
        2. Context block: numbered retrieved chunks [1], [2], ... with source metadata
        3. User query + conversation history (multi-turn)
    • Returns: formatted messages list for LLM
    │
    ▼
[Generate] generation.py
    • Model: GPT-5.5 (OpenAI)
    • Streaming: True (yields token chunks via async generator)
    • Returns: streamed answer tokens + final structured citations list
    • Citation format: [{citation_number, source_file, page_number, excerpt}]
```

---

## 9. Citations Strategy

Citations are a **first-class feature**. Every assistant response must include traceable
references to the source documents used in generation.

**Storage (ChromaDB metadata per chunk):**
```json
{
  "source_file": "contract_law_2024.pdf",
  "page_number": 14,
  "chunk_id": "contract_law_2024_p14_c2",
  "excerpt": "First 200 chars of chunk text..."
}
```

**Augmentation format (context block sent to LLM):**
```
[1] Source: contract_law_2024.pdf, Page 14
"...chunk text here..."

[2] Source: us_code_title18.pdf, Page 203
"...chunk text here..."
```

**System prompt instruction to LLM:**
> "When answering, cite relevant sources using [1], [2], etc. notation inline.
>  At the end of your response, list all cited sources."

**Response structure returned by generation.py:**
```json
{
  "answer": "streamed text with inline [1] [2] citations...",
  "citations": [
    {
      "number": 1,
      "source_file": "contract_law_2024.pdf",
      "page_number": 14,
      "excerpt": "..."
    }
  ]
}
```

**Persistence:** Citations are stored in the `citations` SQLite table linked to the
`messages` table so past conversations show their original citations.

**UI:** CitationList renders below each assistant message as expandable CitationCard
components showing source file, page number, and the relevant excerpt.

---

## 10. Streaming Strategy

**Protocol:** Server-Sent Events (SSE) over HTTP.

**Backend (FastAPI):**
- Route `POST /conversations/{id}/messages` returns a `StreamingResponse`
- Content-Type: `text/event-stream`
- Token chunks emitted as: `data: {"type": "token", "content": "..."}\n\n`
- Citations emitted at stream end as: `data: {"type": "citations", "content": [...]}\n\n`
- Stream closed with: `data: {"type": "done"}\n\n`

**Client:**
- `useStreaming` hook uses the `fetch` API with `ReadableStream`
- Tokens appended to `StreamingMessage` in real-time
- On `citations` event: CitationList rendered below the message
- On `done` event: message persisted to Zustand store + SQLite

---

## 11. Database Schema (SQLite)

```sql
-- Tracks each chat session
CREATE TABLE conversations (
    id          TEXT PRIMARY KEY,           -- UUID
    title       TEXT NOT NULL,              -- Auto-generated from first message
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Individual messages within a conversation
CREATE TABLE messages (
    id              TEXT PRIMARY KEY,       -- UUID
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Citations linked to assistant messages
CREATE TABLE citations (
    id          TEXT PRIMARY KEY,           -- UUID
    message_id  TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    number      INTEGER NOT NULL,           -- Citation number [1], [2], etc.
    source_file TEXT NOT NULL,
    page_number INTEGER,
    excerpt     TEXT,
    chunk_id    TEXT
);

-- Tracks uploaded documents and ingestion status
CREATE TABLE documents (
    id          TEXT PRIMARY KEY,           -- UUID
    filename    TEXT NOT NULL,
    file_path   TEXT NOT NULL,
    status      TEXT NOT NULL CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
    error       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 12. API Endpoints

### Conversations
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/conversations` | List all conversations (id, title, updated_at) |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/{id}` | Get conversation with full message + citation history |
| `DELETE` | `/api/conversations/{id}` | Delete conversation and all messages |
| `PATCH` | `/api/conversations/{id}` | Update conversation title |

### Messages (Streaming)
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/conversations/{id}/messages` | Send user message → SSE streamed assistant response |

### Documents
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload PDF, trigger ingestion pipeline |
| `GET` | `/api/documents` | List all documents with ingestion status |
| `GET` | `/api/documents/{id}` | Get single document status |
| `DELETE` | `/api/documents/{id}` | Delete document (does NOT remove from vector store in v1) |

### System
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |

---

## 13. Environment Variables

All secrets and configuration live in server-side `.env` files. Never committed to git.

### `lawyergpt-server/.env` (Server + Engine share this key)
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./lawyergpt.db

# AI Layer
OPENAI_API_KEY=sk-...

# App
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# CORS
FRONTEND_ORIGIN=http://localhost:5173

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
```

### `lawyergpt-engine/.env` (Engine-specific config)
```env
# OpenAI
OPENAI_API_KEY=sk-...

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=lawyergpt_docs

# Retrieval
TOP_K_RESULTS=5

# Ingestion
BATCH_SIZE=100
CHUNK_SIZE=2000
CHUNK_OVERLAP=100
EMBEDDING_MODEL=text-embedding-3-large

# Generation
GENERATION_MODEL=gpt-5.5
```

---

## 14. Logging & Exception Handling

### Logging
- **Format:** Structured JSON logs (machine-readable for production)
- **Library:** Python `logging` with a custom JSON formatter
- **Levels:** DEBUG (dev), INFO (prod default), WARNING, ERROR, CRITICAL
- **Fields logged:** timestamp, level, module, function, message, request_id (where applicable)
- **Log points:**
  - Every API request (method, path, status, duration)
  - Ingestion pipeline: per-batch progress, document status transitions
  - Query pipeline: retrieval count, generation start/end
  - All caught exceptions with stack traces

### Exception Handling
- **Custom exceptions** defined in `core/exceptions.py` per layer
- **Global error handler middleware** in FastAPI maps exceptions → HTTP responses
- **Engine exceptions** bubble up to the service layer and are caught before streaming begins
- **Ingestion errors** update `documents.status = 'failed'` with `documents.error` detail
- **Never expose raw stack traces** to the client — sanitized error messages only

```python
# Exception hierarchy (backend)
class LawyerGPTException(Exception): ...
class DocumentNotFoundError(LawyerGPTException): ...
class IngestionError(LawyerGPTException): ...
class VectorStoreError(LawyerGPTException): ...
class GenerationError(LawyerGPTException): ...
```

---

## 15. Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Same Python process for server + engine | Yes | Simplifies local dev, avoids inter-service latency |
| Separate repos | Yes | Clean separation of concerns, independent versioning |
| SQLite | Phase 1 | Zero-ops local dev; schema designed for easy Postgres migration |
| ChromaDB local | Phase 1 | No infrastructure required; persistent on disk |
| SSE over WebSockets | SSE | Simpler, HTTP-native, sufficient for unidirectional streaming |
| Citations as first-class DB entity | Yes | Enables past conversation replay with original citations |
| Batch ingestion (100/batch) | Yes | Avoids OpenAI rate limits; allows progress tracking |
| UV for dependency management | Yes | Fast, deterministic, PEP-compliant |
| No authentication (Phase 1) | Yes | Simplifies initial build; auth layer added in future phase |

---

## 16. Coding Standards

- **Routes:** Thin — only request parsing and response formatting. No business logic.
- **Services:** All business logic lives here. Services call AI layer functions directly.
- **Models:** SQLAlchemy ORM models only. No logic.
- **Schemas:** Pydantic models for all request/response validation.
- **No code duplication:** Shared utilities go in `core/`.
- **Async throughout:** All FastAPI routes, service methods, and DB calls are `async`.
- **Type hints:** Required on all function signatures in Python.
- **No bare `except`:** Always catch specific exception types.
- **Environment config:** All configuration via `pydantic-settings`; no hardcoded values.
- **Engine is stateless:** No shared mutable state; ChromaDB client is a singleton.

---

## 17. Skills

Skills are opt-in communication or behaviour modes. Full instructions live in their own
files — read the file on first trigger, then keep the rules active for the session.

| Skill | File | Trigger |
|---|---|---|
| **caveman** | [skills/caveman/SKILL.md](skills/caveman/SKILL.md) | User says "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or types `/caveman` |

**How to use a skill:**
1. When a trigger phrase is detected, read the skill file listed above.
2. Apply the rules defined in that file for all subsequent responses.
3. Stay in the mode until the skill's own exit condition is met (e.g. "stop caveman" / "normal mode").
