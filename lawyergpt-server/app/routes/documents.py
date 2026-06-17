from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_session
from app.schemas.document_schema import DocumentResponse
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    content = await file.read()
    return await document_service.upload_document(
        session=session,
        filename=file.filename or "upload.pdf",
        content=content,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: AsyncSession = Depends(get_session),
) -> list[DocumentResponse]:
    return await document_service.list_documents(session)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    return await document_service.get_document(session, document_id)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    await document_service.delete_document(session, document_id)
