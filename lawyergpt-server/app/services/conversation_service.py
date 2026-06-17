import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConversationNotFoundError
from app.core.logging import get_logger
from app.models.conversation import Conversation
from app.schemas.conversation_schema import ConversationResponse, ConversationSummary

logger = get_logger(__name__)


async def list_conversations(session: AsyncSession) -> list[ConversationSummary]:
    result = await session.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return [ConversationSummary.model_validate(c) for c in conversations]


async def create_conversation(session: AsyncSession, title: str = "New Chat") -> ConversationResponse:
    conversation = Conversation(id=str(uuid.uuid4()), title=title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    logger.info("Created conversation %s", conversation.id)
    return ConversationResponse.model_validate(conversation)


async def get_conversation(session: AsyncSession, conversation_id: str) -> ConversationResponse:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
    return ConversationResponse.model_validate(conversation)


async def delete_conversation(session: AsyncSession, conversation_id: str) -> None:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
    await session.delete(conversation)
    await session.commit()
    logger.info("Deleted conversation %s", conversation_id)


async def rename_conversation(
    session: AsyncSession, conversation_id: str, title: str
) -> ConversationResponse:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
    conversation.title = title
    conversation.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(conversation)
    return ConversationResponse.model_validate(conversation)
