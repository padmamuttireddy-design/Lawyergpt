from __future__ import annotations

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

_client = None
_collection = None


def get_client():
    global _client
    if _client is None:
        import chromadb  # lazy import
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        logger.info("ChromaDB client initialised at %s", settings.chroma_persist_dir)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Using ChromaDB collection: %s", settings.chroma_collection_name)
    return _collection
