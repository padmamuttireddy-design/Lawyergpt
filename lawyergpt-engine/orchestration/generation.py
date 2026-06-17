from __future__ import annotations

import re
from collections.abc import AsyncGenerator

from core.config import settings
from core.exceptions import GenerationError
from core.logging import get_logger
from orchestration.augmentation import build_messages
from orchestration.retriever import RetrievedChunk, retrieve

logger = get_logger(__name__)

# OpenAI client is created once and reused (lazy — avoids import errors at startup)
_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import AsyncOpenAI
        if not settings.openai_api_key or settings.openai_api_key.startswith("sk-placeholder"):
            raise GenerationError("OPENAI_API_KEY is not configured in .env")
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def stream_answer(
    query: str,
    history: list[dict] | None = None,
    model: str | None = None,
) -> AsyncGenerator[dict, None]:
    """
    Full RAG pipeline: retrieve → augment → generate → extract citations.

    Yields (in order):
        {"type": "token",     "content": "<text>"}   — one per streamed token
        {"type": "citations", "content": [...]     }  — after stream ends
        {"type": "done"}                              — signals end of stream
    """
    model_id = model or settings.generation_model

    # ── STEP 1: Retrieve ──────────────────────────────────────────────────
    logger.info("STEP 1 — Retrieving relevant chunks for query: %s", query[:80])
    try:
        chunks: list[RetrievedChunk] = retrieve(query)
    except Exception as exc:
        raise GenerationError(f"Retrieval step failed: {exc}") from exc

    logger.info("STEP 1 — Retrieved %d chunk(s)", len(chunks))

    # ── STEP 2: Augment ───────────────────────────────────────────────────
    logger.info("STEP 2 — Building augmented prompt (system + context + question)")
    messages = build_messages(
        user_query=query,
        retrieved_chunks=chunks,
        history=history,
    )
    logger.info("STEP 2 — Prompt ready: %d message(s) in context", len(messages))

    # ── STEP 3: Generate (stream) ─────────────────────────────────────────
    logger.info("STEP 3 — Streaming response from model: %s", model_id)
    full_response: list[str] = []

    try:
        client = _get_client()
        stream = await client.chat.completions.create(
            model=model_id,
            messages=messages,  # type: ignore[arg-type]
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                full_response.append(delta.content)
                yield {"type": "token", "content": delta.content}

    except Exception as exc:
        raise GenerationError(f"LLM generation failed: {exc}") from exc

    response_text = "".join(full_response)
    logger.info("STEP 3 — Generation complete. Response length: %d chars", len(response_text))

    # ── STEP 4: Extract citations ─────────────────────────────────────────
    # Only return citations if the LLM actually answered (not a relevance refusal).
    # Then filter to only the [N] numbers the LLM actually referenced inline.
    logger.info("STEP 4 — Extracting citations from response")

    is_refusal = "I can only assist with legal questions" in response_text
    if is_refusal:
        logger.info("STEP 4 — Relevance refusal detected. Returning 0 citations.")
        citations: list[dict] = []
    else:
        cited_numbers = {int(n) for n in re.findall(r"\[(\d+)\]", response_text)}
        citations = [
            {
                "number": i + 1,
                "source_file": c.source_file,
                "page_number": c.page_number,
                "excerpt": c.excerpt,
                "chunk_id": c.chunk_id,
            }
            for i, c in enumerate(chunks)
            if (i + 1) in cited_numbers
        ]
        logger.info(
            "STEP 4 — %d citation(s) extracted from %d available chunks",
            len(citations),
            len(chunks),
        )

    yield {"type": "citations", "content": citations}
    yield {"type": "done"}
