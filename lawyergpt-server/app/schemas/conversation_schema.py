from datetime import datetime

from pydantic import BaseModel

from app.schemas.message_schema import MessageResponse


class ConversationCreate(BaseModel):
    title: str = "New Chat"


class ConversationUpdate(BaseModel):
    title: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}
