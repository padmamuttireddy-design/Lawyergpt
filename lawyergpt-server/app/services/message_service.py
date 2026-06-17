import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConversationNotFoundError
from app.core.logging import get_logger
from app.models.citation import Citation
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message_schema import CitationResponse, MessageResponse
from app.services import ai_bridge

logger = get_logger(__name__)


async def _get_history(session: AsyncSession, conversation_id: str) -> list[dict]:
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in messages]


async def save_user_message(
    session: AsyncSession, conversation_id: str, content: str
) -> MessageResponse:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    if not result.scalar_one_or_none():
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found")

    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=content,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return MessageResponse.model_validate(message)


async def save_assistant_message(
    session: AsyncSession,
    conversation_id: str,
    content: str,
    citations_data: list[dict],
) -> MessageResponse:
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="assistant",
        content=content,
    )
    session.add(message)
    await session.flush()

    for c in citations_data:
        citation = Citation(
            id=str(uuid.uuid4()),
            message_id=message.id,
            number=c.get("number", 0),
            source_file=c.get("source_file", ""),
            page_number=c.get("page_number"),
            excerpt=c.get("excerpt"),
            chunk_id=c.get("chunk_id"),
        )
        session.add(citation)

    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(message)
    return MessageResponse.model_validate(message)


async def stream_message(
    session: AsyncSession,
    conversation_id: str,
    user_content: str,
    model: str,
) -> AsyncGenerator[str, None]:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    if not result.scalar_one_or_none():
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found")

    await save_user_message(session, conversation_id, user_content)
    history = await _get_history(session, conversation_id)

    full_content: list[str] = []
    final_citations: list[dict] = []

    import json

    async def _generate() -> AsyncGenerator[str, None]:
        async for chunk in ai_bridge.stream_response(conversation_id, user_content, model, history):
            if chunk.startswith("data: "):
                raw = chunk[6:].strip()
                try:
                    event = json.loads(raw)
                    if event["type"] == "token":
                        full_content.append(event["content"])
                    elif event["type"] == "citations":
                        final_citations.extend(event["content"])
                    elif event["type"] == "done":
                        assembled = "".join(full_content)
                        saved = await save_assistant_message(
                            session, conversation_id, assembled, final_citations
                        )
                        import json as _json
                        done_payload = _json.dumps({"type": "done", "message": saved.model_dump(mode="json")})
                        yield f"data: {done_payload}\n\n"
                        return
                except (json.JSONDecodeError, KeyError):
                    pass
            yield chunk

    return _generate()
