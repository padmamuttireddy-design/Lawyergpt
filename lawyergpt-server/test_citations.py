import asyncio, httpx, json

async def ask(question, label):
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post("http://localhost:8000/api/conversations", json={})
        conv_id = r.json()["id"]
        url = f"http://localhost:8000/api/conversations/{conv_id}/messages"
        print(f"\n--- {label} ---")
        print(f"Q: {question}")
        print("A: ", end="", flush=True)
        citations = []
        async with client.stream("POST", url, json={"content": question, "model": "gpt-4o"}) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data["type"] == "token":
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "citations":
                        citations = data["content"]
                    elif data["type"] == "done":
                        print()
                        break
        print(f"Citations returned: {len(citations)}")
        for c in citations:
            print(f"  [{c['number']}] {c['source_file']} p.{c['page_number']}")

async def main():
    await ask("What are the elements of negligence?", "LEGAL QUESTION")
    await ask("How do I bake a chocolate cake?", "NON-LEGAL QUESTION")

asyncio.run(main())
