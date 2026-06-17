"""CLI: ingest all PDFs in a directory into ChromaDB.

Usage:
    python scripts/ingest.py ./path/to/pdfs
    python scripts/ingest.py ./path/to/pdfs --pattern "*.pdf"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.logging import get_logger, setup_logging
from ingestion.chunker import chunk_documents
from ingestion.loader import load_pdf
from ingestion.vector_store_loader import load_chunks

setup_logging("INFO")
logger = get_logger(__name__)


def ingest_directory(directory: str, pattern: str = "*.pdf") -> None:
    pdf_dir = Path(directory)
    if not pdf_dir.exists():
        logger.error("Directory not found: %s", directory)
        sys.exit(1)

    pdf_files = list(pdf_dir.glob(pattern))
    if not pdf_files:
        logger.warning("No PDFs found in %s matching pattern %s", directory, pattern)
        return

    logger.info("Found %d PDF(s) to ingest", len(pdf_files))

    for pdf_path in pdf_files:
        logger.info("Processing: %s", pdf_path.name)
        try:
            docs = load_pdf(str(pdf_path))
            chunks = chunk_documents(docs)
            load_chunks(chunks)
            logger.info("Done: %s (%d chunks)", pdf_path.name, len(chunks))
        except Exception as exc:
            logger.error("Failed to ingest %s: %s", pdf_path.name, exc)

    logger.info("Ingestion complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDF documents into ChromaDB")
    parser.add_argument("directory", help="Path to directory containing PDF files")
    parser.add_argument("--pattern", default="*.pdf", help="Glob pattern for files (default: *.pdf)")
    args = parser.parse_args()
    ingest_directory(args.directory, args.pattern)
