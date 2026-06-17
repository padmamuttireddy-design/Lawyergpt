from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ConversationNotFoundError,
    DocumentNotFoundError,
    FileTooLargeError,
    IngestionError,
    InvalidFileTypeError,
    LawyerGPTException,
    MessageNotFoundError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ConversationNotFoundError)
    async def conversation_not_found(_: Request, exc: ConversationNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Conversation not found"})

    @app.exception_handler(MessageNotFoundError)
    async def message_not_found(_: Request, exc: MessageNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Message not found"})

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found(_: Request, exc: DocumentNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Document not found"})

    @app.exception_handler(FileTooLargeError)
    async def file_too_large(_: Request, exc: FileTooLargeError) -> JSONResponse:
        return JSONResponse(status_code=413, content={"detail": str(exc) or "File too large"})

    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type(_: Request, exc: InvalidFileTypeError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc) or "Invalid file type"})

    @app.exception_handler(IngestionError)
    async def ingestion_error(_: Request, exc: IngestionError) -> JSONResponse:
        logger.error("Ingestion error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Document ingestion failed"})

    @app.exception_handler(LawyerGPTException)
    async def lawyergpt_error(_: Request, exc: LawyerGPTException) -> JSONResponse:
        logger.error("Unhandled domain error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.exception_handler(Exception)
    async def unhandled_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
