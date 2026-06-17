import asyncio, httpx, json

async def ask(question, label):
    # Create a fresh conversation for each test
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post("http://localhost:8000/api/conversations", json={})
        conv_id = r.json()["id"]
        
        url = f"http://localhost:8000/api/conversations/{conv_id}/messages"
        body = {"content": question, "model": "gpt-4o"}
        print(f"\n--- {label} ---")
        print(f"Q: {question}")
        print("A: ", end="", flush=True)
        async with client.stream("POST", url, json=body) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data["type"] == "token":
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "done":
                        print()
                        break

async def main():
    await ask("What is a tort?", "LEGAL QUESTION")
    await ask("What is the best recipe for pasta?", "NON-LEGAL QUESTION")

asyncio.run(main())
