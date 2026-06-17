import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import DocumentNotFoundError, FileTooLargeError, InvalidFileTypeError
from app.core.logging import get_logger
from app.models.document import Document
from app.schemas.document_schema import DocumentResponse

logger = get_logger(__name__)


def _ensure_upload_dir() -> Path:
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


async def upload_document(
    session: AsyncSession,
    filename: str,
    content: bytes,
) -> DocumentResponse:
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileTypeError("Only PDF files are supported")

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise FileTooLargeError(
            f"File exceeds maximum allowed size of {settings.max_file_size_mb} MB"
        )

    upload_dir = _ensure_upload_dir()
    doc_id = str(uuid.uuid4())
    safe_name = f"{doc_id}_{filename}"
    file_path = upload_dir / safe_name

    file_path.write_bytes(content)
    logger.info("Saved uploaded file to %s", file_path)

    document = Document(
        id=doc_id,
        filename=filename,
        file_path=str(file_path),
        status="pending",
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    # Fire-and-forget ingestion (stub for now — engine will be wired in Phase 3)
    logger.info("Document %s queued for ingestion", doc_id)

    return DocumentResponse.model_validate(document)


async def list_documents(session: AsyncSession) -> list[DocumentResponse]:
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


async def get_document(session: AsyncSession, document_id: str) -> DocumentResponse:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise DocumentNotFoundError(f"Document {document_id} not found")
    return DocumentResponse.model_validate(document)


async def delete_document(session: AsyncSession, document_id: str) -> None:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise DocumentNotFoundError(f"Document {document_id} not found")

    file_path = Path(document.file_path)
    if file_path.exists():
        os.remove(file_path)

    await session.delete(document)
    await session.commit()
    logger.info("Deleted document %s", document_id)
