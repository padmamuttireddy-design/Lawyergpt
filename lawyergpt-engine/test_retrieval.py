"""
Retrieval Phase Test
--------------------
Run this script to inspect exactly what chunks are retrieved from the
vector database for any given query.

Usage:
    .\.venv\Scripts\python.exe test_retrieval.py
    .\.venv\Scripts\python.exe test_retrieval.py "your custom question here"
"""

import sys
import os

# Allow running from the engine directory without package installation
sys.path.insert(0, os.path.dirname(__file__))

# Fix SSL certificate verification on Windows
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from orchestration.retriever import retrieve
from core.config import settings


DIVIDER = "=" * 70
THIN    = "-" * 70


def relevance_bar(score: float, width: int = 20) -> str:
    """Visual bar showing similarity score."""
    filled = int(score * width)
    bar = "#" * filled + "." * (width - filled)
    return f"[{bar}] {score:.3f}"


def test_retrieval(query: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  RETRIEVAL PHASE TEST")
    print(DIVIDER)
    print(f"  Query       : {query}")
    print(f"  Top-K       : {settings.top_k_results}")
    print(f"  Min Score   : {settings.min_relevance_score}")
    print(f"  Vector DB   : {settings.chroma_persist_dir}")
    print(f"  Collection  : {settings.chroma_collection_name}")
    print(DIVIDER)

    print("\nEmbedding query and searching vector database...\n")

    chunks = retrieve(query)

    if not chunks:
        print("  No relevant chunks found above the relevance threshold.")
        print(f"  (All retrieved chunks scored below {settings.min_relevance_score})")
        print(f"\n  Tip: Lower MIN_RELEVANCE_SCORE in .env to see more results.\n")
        return

    print(f"  Found {len(chunks)} relevant chunk(s):\n")

    for i, chunk in enumerate(chunks, start=1):
        print(f"{THIN}")
        print(f"  Chunk #{i}")
        print(f"  Source      : {chunk.source_file}")
        print(f"  Page        : {chunk.page_number}")
        print(f"  Chunk ID    : {chunk.chunk_id}")
        print(f"  Relevance   : {relevance_bar(chunk.score)}")
        print(f"\n  Full Text:")
        print(f"  {'-'*50}")
        # Indent each line of the chunk text
        for line in chunk.text.strip().splitlines():
            print(f"    {line}")
        print()

    print(DIVIDER)
    print(f"  SUMMARY: {len(chunks)} chunk(s) will be passed to the LLM as context.")
    print(DIVIDER)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Default test queries — edit or extend as needed
        test_queries = [
            "What are the elements of a valid contract?",
            "What is negligence in tort law?",
            "What are the penalties for criminal offenses?",
        ]
        print("\nNo query provided — running default test queries.\n")
        print("Usage: .venv\\Scripts\\python.exe test_retrieval.py \"your question\"")
        for q in test_queries:
            test_retrieval(q)
        sys.exit(0)

    test_retrieval(query)
