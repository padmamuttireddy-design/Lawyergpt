from datetime import datetime

from pydantic import BaseModel


class CitationResponse(BaseModel):
    id: str
    number: int
    source_file: str
    page_number: int | None = None
    excerpt: str | None = None
    chunk_id: str | None = None

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    role: str = "user"
    content: str
    model: str = "gpt-4o"


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    citations: list[CitationResponse] = []

    model_config = {"from_attributes": True}
