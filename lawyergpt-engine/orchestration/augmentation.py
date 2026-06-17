import os

from orchestration.retriever import RetrievedChunk

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_prompt(filename: str) -> str:
    path = os.path.join(_PROMPTS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


SYSTEM_PROMPT: str = _load_prompt("system_prompt.txt")


def build_messages(
    user_query: str,
    retrieved_chunks: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> list[dict]:
    """
    Compose the full messages list for the LLM.

    Structure:
      [0] system  — role definition + citation instructions (loaded from prompts/system_prompt.txt)
      [1..n-1]    — conversation history (last 10 turns, if any)
      [n] user    — context block (numbered retrieved chunks) + user question
    """
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-10:])

    user_content = _build_user_message(user_query, retrieved_chunks)
    messages.append({"role": "user", "content": user_content})

    return messages


def _build_user_message(user_query: str, chunks: list[RetrievedChunk]) -> str:
    """Combine the context block and the user question into one user message."""
    context = _build_context_block(chunks)
    return f"{context}\n\n---\n\nQuestion: {user_query}"


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    """
    Format retrieved chunks as a numbered context block for the LLM.

    Example output:
        CONTEXT — 2 source document(s) retrieved:

        [1] Source: contract_law.pdf | Page: 14
        "...chunk text..."

        [2] Source: us_code.pdf | Page: 203
        "...chunk text..."
    """
    if not chunks:
        return "CONTEXT — No relevant source documents were found for this query."

    lines = [f"CONTEXT — {len(chunks)} source document(s) retrieved:\n"]
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"[{i}] Source: {chunk.source_file} | Page: {chunk.page_number}")
        lines.append(f'"{chunk.text}"\n')

    return "\n".join(lines)
