from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.schemas.message_schema import MessageCreate
from app.services import message_service

router = APIRouter(prefix="/api/conversations", tags=["messages"])


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: MessageCreate,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    stream = await message_service.stream_message(
        session=session,
        conversation_id=conversation_id,
        user_content=body.content,
        model=body.model,
    )
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
