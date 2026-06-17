import asyncio
from orchestration.retriever import retrieve
from orchestration.augmentation import build_messages
from orchestration.generation import stream_answer


async def test_query(question: str):
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print('='*60)

    # Step 1 - Retrieve
    print("\n=== STEP 1: RETRIEVING RELEVANT CHUNKS ===")
    chunks = retrieve(question)
    print(f"Found {len(chunks)} relevant chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\n[{i+1}] {chunk.source_file} — Page {chunk.page_number} (score: {chunk.score:.3f})")
        print(chunk.excerpt[:200])

    # Step 2 - Augment
    print("\n=== STEP 2: BUILDING PROMPT ===")
    messages = build_messages(question, chunks)
    print(f"Built {len(messages)} messages for LLM")

    # Step 3 - Generate
    print("\n=== STEP 3: GENERATING ANSWER ===")
    full_answer = ""
    citations = []
    async for event in stream_answer(question):
        if event["type"] == "token":
            print(event["content"], end="", flush=True)
            full_answer += event["content"]
        elif event["type"] == "citations":
            citations = event["content"]
        elif event["type"] == "done":
            break

    print(f"\n\n=== CITATIONS ===")
    for c in citations:
        print(f"[{c['number']}] {c['source_file']} — Page {c['page_number']}")
        print(f"    {c['excerpt'][:150]}")


if __name__ == "__main__":
    asyncio.run(test_query("What are the elements required for a valid contract?"))
