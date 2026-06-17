from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.schemas.conversation_schema import (
    ConversationResponse,
    ConversationSummary,
    ConversationUpdate,
)
from app.services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    session: AsyncSession = Depends(get_session),
) -> list[ConversationSummary]:
    return await conversation_service.list_conversations(session)


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    return await conversation_service.create_conversation(session)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    return await conversation_service.get_conversation(session, conversation_id)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    await conversation_service.delete_conversation(session, conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: str,
    body: ConversationUpdate,
    session: AsyncSession = Depends(get_session),
) -> ConversationResponse:
    return await conversation_service.rename_conversation(session, conversation_id, body.title)
