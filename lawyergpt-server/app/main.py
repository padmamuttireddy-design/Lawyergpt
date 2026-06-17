import sys
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

# Inject Windows system certificates into Python's SSL so OpenAI API calls succeed
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from fastapi import FastAPI

# Ensure engine packages (query, ingestion, core) are importable
_engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lawyergpt-engine"))
if _engine_path not in sys.path:
    sys.path.insert(0, _engine_path)

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.db import create_tables
from app.middleware.cors import add_cors
from app.middleware.error_handler import add_error_handlers
from app.routes import conversations, documents, health, messages

setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await create_tables()
    yield


app = FastAPI(title="LawyerGPT API", version="0.1.0", lifespan=lifespan)

add_cors(app)
add_error_handlers(app)

# ── System ──────────────────────────────────────────────
# GET  /api/health
app.include_router(health.router)

# ── Conversations ────────────────────────────────────────
# GET    /api/conversations
# POST   /api/conversations
# GET    /api/conversations/{id}
# DELETE /api/conversations/{id}
# PATCH  /api/conversations/{id}
app.include_router(conversations.router)

# ── Messages (SSE streaming) ─────────────────────────────
# POST   /api/conversations/{id}/messages
app.include_router(messages.router)

# ── Documents ────────────────────────────────────────────
# POST   /api/documents/upload
# GET    /api/documents
# GET    /api/documents/{id}
# DELETE /api/documents/{id}
app.include_router(documents.router)
