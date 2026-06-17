from __future__ import annotations

from core.config import settings
from core.exceptions import EmbeddingError
from core.logging import get_logger

logger = get_logger(__name__)

_embeddings = None


def get_embeddings():
    """Return a singleton OpenAIEmbeddings instance."""
    global _embeddings
    if _embeddings is None:
        from langchain_openai import OpenAIEmbeddings  # lazy import
        if not settings.openai_api_key or settings.openai_api_key == "sk-placeholder":
            raise EmbeddingError("OPENAI_API_KEY is not set in .env")
        _embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        logger.info("Embeddings initialised with model: %s", settings.embedding_model)
    return _embeddings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of text strings and return their vectors."""
    if not texts:
        raise EmbeddingError("No texts provided for embedding")
    try:
        embeddings = get_embeddings()
        vectors = embeddings.embed_documents(texts)
        logger.info("Embedded %d texts", len(texts))
        return vectors
    except Exception as exc:
        raise EmbeddingError(f"Embedding failed: {exc}") from exc


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    try:
        embeddings = get_embeddings()
        vector = embeddings.embed_query(text)
        return vector
    except Exception as exc:
        raise EmbeddingError(f"Query embedding failed: {exc}") from exc
