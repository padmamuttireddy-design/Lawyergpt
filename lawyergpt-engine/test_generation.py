"""
Generation Phase Test
---------------------
Runs the full RAG pipeline end-to-end:
  Retrieve → Augment → Generate → Extract Citations

Streams the LLM response live to the terminal, then prints citations.

Usage:
    .venv\Scripts\python.exe test_generation.py
    .venv\Scripts\python.exe test_generation.py "your custom question here"
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(__file__))

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from orchestration.generation import stream_answer
from core.config import settings

DIVIDER = "=" * 70
SECTION = "-" * 70


async def test_generation(query: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  GENERATION PHASE TEST  —  Full RAG Pipeline")
    print(DIVIDER)
    print(f"  Query : {query}")
    print(f"  Model : {settings.generation_model}")
    print(DIVIDER)

    print("\n[STEP 1] Retrieving chunks from vector database...")
    print("[STEP 2] Building augmented prompt...")
    print("[STEP 3] Streaming response from LLM...\n")
    print(SECTION)
    print("  RESPONSE")
    print(SECTION)

    citations = []
    token_count = 0

    async for event in stream_answer(query=query):
        if event["type"] == "token":
            print(event["content"], end="", flush=True)
            token_count += 1
        elif event["type"] == "citations":
            citations = event["content"]
        elif event["type"] == "done":
            break

    print(f"\n{SECTION}")
    print(f"  Streamed {token_count} token(s)")

    # ── Citations ─────────────────────────────────────────────────────────
    print(f"\n[STEP 4] Citations extracted: {len(citations)}\n")

    if citations:
        print(SECTION)
        print("  CITATIONS")
        print(SECTION)
        for c in citations:
            print(f"\n  [{c['number']}] {c['source_file']}  |  Page {c['page_number']}")
            print(f"  Chunk ID : {c['chunk_id']}")
            excerpt = c.get("excerpt", "")
            if excerpt:
                print(f"  Excerpt  : {excerpt[:200]}{'...' if len(excerpt) > 200 else ''}")
    else:
        print("  No citations returned.")

    print(f"\n{DIVIDER}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("\nNo query provided — running default test queries.\n")
        print("Usage: .venv\\Scripts\\python.exe test_generation.py \"your question\"\n")
        query = "What are the elements of a valid contract?"

    asyncio.run(test_generation(query))
