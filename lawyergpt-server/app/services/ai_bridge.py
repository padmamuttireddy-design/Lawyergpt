import json
from collections.abc import AsyncGenerator

from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from orchestration.generation import stream_answer as _stream_answer
    _engine_available = True
    logger.info("Engine loaded successfully")
except Exception as exc:
    _engine_available = False
    _engine_error = str(exc)
    logger.error("Engine failed to load: %s", exc, exc_info=True)


async def stream_response(
    conversation_id: str,
    user_content: str,
    model: str,
    history: list[dict],
) -> AsyncGenerator[str, None]:
    """Call the engine query pipeline and yield SSE-formatted strings."""
    logger.info("Streaming response for conversation %s using model %s", conversation_id, model)

    if not _engine_available:
        error_event = json.dumps({"type": "token", "content": f"[Engine error: {_engine_error}]"})
        yield f"data: {error_event}\n\n"
        yield f"data: {json.dumps({'type': 'citations', 'content': []})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    try:
        async for event in _stream_answer(query=user_content, history=history, model=model):
            yield f"data: {json.dumps(event)}\n\n"
    except Exception as exc:
        logger.error("Generation error: %s", exc, exc_info=True)
        error_event = json.dumps({"type": "token", "content": f"[Generation error: {exc}]"})
        yield f"data: {error_event}\n\n"
        yield f"data: {json.dumps({'type': 'citations', 'content': []})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
