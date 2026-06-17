import asyncio, httpx, json

async def test():
    convId = "d6449230-4b1a-4dbb-91e5-c184444dadda"
    url = f"http://localhost:8000/api/conversations/{convId}/messages"
    body = {"content": "What are the elements of a valid contract?", "model": "gpt-4o"}
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, json=body) as resp:
            print("Status:", resp.status_code)
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data["type"] == "token":
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "citations":
                        print("\n\n--- CITATIONS ---")
                        for c in data["content"]:
                            num = c["number"]
                            src = c["source_file"]
                            pg = c["page_number"]
                            ex = c["excerpt"][:80]
                            print(f"[{num}] {src} p.{pg}  {ex}...")
                    elif data["type"] == "done":
                        print("\n--- DONE ---")
                        break

asyncio.run(test())
