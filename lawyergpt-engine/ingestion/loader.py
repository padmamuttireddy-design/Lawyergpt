from __future__ import annotations

from pathlib import Path

from core.exceptions import LoaderError
from core.logging import get_logger

logger = get_logger(__name__)

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "lawyergpt-server" / "uploads"


def load_pdf(file_path: str) -> list:
    """Extract pages from a PDF. Falls back to OCR if standard parsing yields nothing."""
    from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader  # lazy

    path = Path(file_path)
    if not path.exists():
        raise LoaderError(f"File not found: {file_path}")
    if not path.suffix.lower() == ".pdf":
        raise LoaderError(f"Not a PDF file: {file_path}")

    logger.info("Loading PDF: %s", file_path)

    try:
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        if docs and any(d.page_content.strip() for d in docs):
            logger.info("Loaded %d pages from %s via PyPDFLoader", len(docs), path.name)
            return _attach_metadata(docs, path.name)
    except Exception as exc:
        logger.warning("PyPDFLoader failed for %s: %s — falling back to OCR", path.name, exc)

    try:
        logger.info("Trying UnstructuredPDFLoader (OCR) for %s", path.name)
        loader = UnstructuredPDFLoader(str(path), strategy="ocr_only")
        docs = loader.load()
        logger.info("Loaded %d pages from %s via OCR", len(docs), path.name)
        return _attach_metadata(docs, path.name)
    except Exception as exc:
        raise LoaderError(f"Failed to load {path.name}: {exc}") from exc


def load_from_uploads(filename: str, uploads_dir: str | None = None) -> list:
    folder = Path(uploads_dir) if uploads_dir else UPLOADS_DIR
    file_path = folder / filename
    if not file_path.exists():
        matches = list(folder.glob(f"*_{filename}"))
        if matches:
            file_path = matches[0]
            logger.info("Resolved %s to %s", filename, file_path.name)
        else:
            raise LoaderError(f"{filename} not found in uploads folder: {folder}")
    return load_pdf(str(file_path))


def load_all_from_uploads(uploads_dir: str | None = None) -> list:
    folder = Path(uploads_dir) if uploads_dir else UPLOADS_DIR
    if not folder.exists():
        raise LoaderError(f"Uploads folder not found: {folder}")
    pdf_files = list(folder.glob("*.pdf"))
    if not pdf_files:
        raise LoaderError(f"No PDF files found in {folder}")
    all_docs: list = []
    for pdf in pdf_files:
        try:
            docs = load_pdf(str(pdf))
            all_docs.extend(docs)
            logger.info("Loaded %s — %d pages", pdf.name, len(docs))
        except LoaderError as exc:
            logger.error("Skipping %s: %s", pdf.name, exc)
    logger.info("Total pages loaded from uploads: %d", len(all_docs))
    return all_docs


def _attach_metadata(docs: list, filename: str) -> list:
    for i, doc in enumerate(docs):
        doc.metadata["source_file"] = filename
        doc.metadata["filename"] = filename
        if "page" not in doc.metadata:
            doc.metadata["page"] = i
    return docs
