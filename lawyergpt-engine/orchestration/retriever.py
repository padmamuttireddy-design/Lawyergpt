from dataclasses import dataclass

from core.config import settings
from core.exceptions import RetrieverError
from core.logging import get_logger
from core.vector_store import get_collection
from ingestion.embedder import embed_query

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    source_file: str
    page_number: int
    chunk_id: str
    excerpt: str
    score: float


def retrieve(query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    """Embed the query and return the top-k most similar chunks from ChromaDB."""
    k = top_k or settings.top_k_results
    try:
        vector = embed_query(query)
        collection = get_collection()
        results = collection.query(
            query_embeddings=[vector],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise RetrieverError(f"Retrieval failed: {exc}") from exc

    chunks: list[RetrievedChunk] = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for text, meta, dist in zip(documents, metadatas, distances):
        score = float(1 - dist)  # cosine distance → similarity score (0–1)
        if score < settings.min_relevance_score:
            logger.debug("Dropping chunk (score %.3f < threshold %.3f)", score, settings.min_relevance_score)
            continue
        chunks.append(
            RetrievedChunk(
                text=text,
                source_file=meta.get("source_file", ""),
                page_number=int(meta.get("page_number", 0)),
                chunk_id=meta.get("chunk_id", ""),
                excerpt=meta.get("excerpt", text[:200]),
                score=score,
            )
        )
        logger.debug("Chunk accepted: %s p.%s score=%.3f", meta.get("source_file"), meta.get("page_number"), score)

    logger.info("Retrieved %d relevant chunks (threshold=%.2f) for query", len(chunks), settings.min_relevance_score)
    return chunks
