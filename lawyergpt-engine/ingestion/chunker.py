from __future__ import annotations

from core.config import settings
from core.exceptions import ChunkerError
from core.logging import get_logger

logger = get_logger(__name__)


def chunk_documents(docs: list) -> list:
    """Split documents into chunks using recursive character splitting."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # lazy import

    if not docs:
        raise ChunkerError("No documents provided for chunking")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):
        filename = chunk.metadata.get("filename", "unknown")
        page = chunk.metadata.get("page", 0)
        chunk.metadata["chunk_id"] = f"{filename}_p{page}_c{i}"
        chunk.metadata["excerpt"] = chunk.page_content[:200]

    logger.info("Produced %d chunks from %d pages", len(chunks), len(docs))
    return chunks
