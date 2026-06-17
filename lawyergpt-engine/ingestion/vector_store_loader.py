from __future__ import annotations

from core.config import settings
from core.exceptions import VectorStoreError
from core.logging import get_logger
from core.vector_store import get_collection
from ingestion.embedder import embed_texts

logger = get_logger(__name__)


def load_chunks(chunks: list) -> None:
    """Batch upsert document chunks into ChromaDB."""
    if not chunks:
        raise VectorStoreError("No chunks provided for loading")

    collection = get_collection()
    batch_size = settings.batch_size
    total = len(chunks)
    loaded = 0
    failed = 0

    for batch_start in range(0, total, batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        texts = [c.page_content for c in batch]
        ids = [c.metadata["chunk_id"] for c in batch]
        metadatas = [
            {
                "source_file": c.metadata.get("source_file", ""),
                "filename": c.metadata.get("filename", ""),
                "page_number": int(c.metadata.get("page", 0)),
                "chunk_id": c.metadata["chunk_id"],
                "excerpt": c.metadata.get("excerpt", "")[:200],
            }
            for c in batch
        ]

        try:
            vectors = embed_texts(texts)
            collection.upsert(
                ids=ids,
                embeddings=vectors,
                documents=texts,
                metadatas=metadatas,
            )
            loaded += len(batch)
            logger.info(
                "Upserted batch %d–%d / %d",
                batch_start + 1,
                batch_start + len(batch),
                total,
            )
        except Exception as exc:
            failed += len(batch)
            logger.error("Batch %d–%d failed: %s", batch_start + 1, batch_start + len(batch), exc)

    logger.info("Ingestion complete — %d loaded, %d failed", loaded, failed)
    if failed == total:
        raise VectorStoreError("All batches failed during ingestion")
