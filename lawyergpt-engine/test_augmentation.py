"""
Augmentation Phase Test
-----------------------
Run this script to inspect exactly what gets built and passed to the LLM.
It shows all 3 inputs:
  1. System Prompt
  2. Retrieved Context (from retriever)
  3. User Question

Usage:
    .venv\Scripts\python.exe test_augmentation.py
    .venv\Scripts\python.exe test_augmentation.py "your custom question here"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from orchestration.retriever import retrieve
from orchestration.augmentation import SYSTEM_PROMPT, build_messages, _build_context_block
from core.config import settings

DIVIDER = "=" * 70
SECTION = "-" * 70


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def test_augmentation(query: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  AUGMENTATION PHASE TEST")
    print(DIVIDER)
    print(f"  Query      : {query}")
    print(f"  Model      : {settings.generation_model}")
    print(f"  Top-K      : {settings.top_k_results}")
    print(f"  Min Score  : {settings.min_relevance_score}")
    print(DIVIDER)

    # ── STEP 1: Retrieval ──────────────────────────────────────────────────
    print("\n[STEP 1] Running retrieval phase...\n")
    chunks = retrieve(query)
    print(f"  Retrieved {len(chunks)} chunk(s) above threshold {settings.min_relevance_score}")
    if chunks:
        for i, c in enumerate(chunks, 1):
            print(f"  [{i}] {c.source_file} | Page {c.page_number} | Score {c.score:.3f}")

    # ── STEP 2: System Prompt ──────────────────────────────────────────────
    print(f"\n{SECTION}")
    print("  INPUT 1 — SYSTEM PROMPT")
    print(SECTION)
    for line in SYSTEM_PROMPT.strip().splitlines():
        print(f"  {line}")
    print(f"\n  (~{estimate_tokens(SYSTEM_PROMPT)} tokens)")

    # ── STEP 3: Context Block (formatted retrieval results) ────────────────
    context_block = _build_context_block(chunks)
    print(f"\n{SECTION}")
    print("  INPUT 2 — RETRIEVED CONTEXT (formatted for LLM)")
    print(SECTION)
    for line in context_block.strip().splitlines():
        print(f"  {line}")
    print(f"\n  (~{estimate_tokens(context_block)} tokens)")

    # ── STEP 4: User Question ──────────────────────────────────────────────
    print(f"\n{SECTION}")
    print("  INPUT 3 — USER QUESTION")
    print(SECTION)
    print(f"  {query}")
    print(f"\n  (~{estimate_tokens(query)} tokens)")

    # ── STEP 5: Full messages list (what generation.py receives) ───────────
    messages = build_messages(user_query=query, retrieved_chunks=chunks)
    print(f"\n{DIVIDER}")
    print("  FINAL OUTPUT — messages[] passed to generation.py")
    print(DIVIDER)
    total_tokens = 0
    for i, msg in enumerate(messages):
        role = msg["role"].upper()
        content = msg["content"]
        tokens = estimate_tokens(content)
        total_tokens += tokens
        print(f"\n  Message [{i}]  role={role}  (~{tokens} tokens)")
        print(f"  {SECTION}")
        preview = content[:300].replace("\n", "\n  ")
        if len(content) > 300:
            preview += f"\n  ... [{len(content) - 300} more chars]"
        print(f"  {preview}")

    print(f"\n{DIVIDER}")
    print(f"  SUMMARY")
    print(DIVIDER)
    print(f"  Total messages   : {len(messages)}")
    print(f"    [0] system      : 1  (role definition + citation rules)")
    history_count = len(messages) - 2
    if history_count > 0:
        print(f"    [1..{len(messages)-2}] history : {history_count}  (prior conversation turns)")
    print(f"    [{len(messages)-1}] user    : 1  (context block + question)")
    print(f"  Estimated tokens : ~{total_tokens}")
    print(f"  Context chunks   : {len(chunks)}")
    print(DIVIDER)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        test_augmentation(query)
    else:
        print("\nNo query provided — running default test queries.\n")
        print("Usage: .venv\\Scripts\\python.exe test_augmentation.py \"your question\"")
        for q in [
            "What are the elements of a valid contract?",
            "What is negligence in tort law?",
            "What is the weather today?",
        ]:
            test_augmentation(q)
