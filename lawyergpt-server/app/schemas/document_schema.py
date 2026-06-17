from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_path: str
    status: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
