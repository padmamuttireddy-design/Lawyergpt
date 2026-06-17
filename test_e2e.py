"""
End-to-End Test — LawyerGPT
----------------------------
Tests the full stack: Client request → FastAPI server → Engine (RAG) → OpenAI → Response.

Requires the server to be running:
    cd lawyergpt-server
    .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

Usage:
    python test_e2e.py
"""

import sys
import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
DIVIDER  = "=" * 70
SECTION  = "-" * 70
PASS     = "[PASS]"
FAIL     = "[FAIL]"
INFO     = "[INFO]"


def http_get(path: str) -> dict:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def http_post(path: str, body: dict) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def stream_message(conversation_id: str, content: str, model: str = "gpt-4o"):
    """Stream a message and return (full_text, citations)."""
    url = f"{BASE_URL}/api/conversations/{conversation_id}/messages"
    data = json.dumps({"role": "user", "content": content, "model": model}).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    full_text = []
    citations = []
    with urllib.request.urlopen(req, timeout=120) as resp:
        buffer = ""
        while True:
            chunk = resp.read(256)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            lines = buffer.split("\n")
            buffer = lines.pop()
            for line in lines:
                if not line.startswith("data: "):
                    continue
                raw = line[6:].strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if event["type"] == "token":
                    full_text.append(event["content"])
                    print(event["content"], end="", flush=True)
                elif event["type"] == "citations":
                    citations = event["content"]
                elif event["type"] == "done":
                    return "".join(full_text), citations
    return "".join(full_text), citations


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    print(f"  {status}  {label}")
    if detail:
        print(f"         {detail}")
    return condition


results = []

print(f"\n{DIVIDER}")
print("  LawyerGPT — End-to-End Test Suite")
print(DIVIDER)

# ── TEST 1: Health check ───────────────────────────────────────────────────
print(f"\n{'─'*40}")
print("  TEST 1 — Health Check")
print(f"{'─'*40}")
try:
    data = http_get("/api/health")
    ok = check("Server is reachable at :8000", True)
    ok = check("Health status is 'ok'", data.get("status") == "ok", str(data))
    results.append(("Health Check", True))
except Exception as e:
    check("Server is reachable at :8000", False, str(e))
    print(f"\n  {FAIL} Server is not running. Start it with:")
    print("      cd lawyergpt-server")
    print("      .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --port 8000")
    sys.exit(1)

# ── TEST 2: Create conversation ────────────────────────────────────────────
print(f"\n{'─'*40}")
print("  TEST 2 — Create Conversation")
print(f"{'─'*40}")
try:
    conv = http_post("/api/conversations", {"title": "E2E Test"})
    conv_id = conv.get("id")
    ok = check("Conversation created", bool(conv_id), f"id={conv_id}")
    ok = check("Has title field",      "title" in conv)
    ok = check("Has created_at field", "created_at" in conv)
    results.append(("Create Conversation", bool(conv_id)))
except Exception as e:
    check("Create conversation", False, str(e))
    results.append(("Create Conversation", False))
    conv_id = None

# ── TEST 3: Legal question → answer + citations ────────────────────────────
print(f"\n{'─'*40}")
print("  TEST 3 — Legal Question (expects answer + citations)")
print(f"{'─'*40}")
if conv_id:
    try:
        query = "What are the elements of a valid contract?"
        print(f"  {INFO} Query : {query}")
        print(f"  {INFO} Streaming response:\n")
        print(f"  {SECTION}")
        t0 = time.time()
        text, citations = stream_message(conv_id, query)
        elapsed = time.time() - t0
        print(f"\n  {SECTION}")

        ok1 = check("Response received",         len(text) > 0, f"{len(text)} chars in {elapsed:.1f}s")
        ok2 = check("Response is not a refusal", "I can only assist with legal questions" not in text)
        ok3 = check("Citations returned",         len(citations) > 0, f"{len(citations)} citation(s)")
        ok4 = check("Citation has source_file",   all("source_file" in c for c in citations))
        ok5 = check("Citation has page_number",   all("page_number" in c for c in citations))

        if citations:
            print(f"\n  {INFO} Citations found:")
            for c in citations:
                print(f"       [{c['number']}] {c['source_file']} | Page {c['page_number']}")

        results.append(("Legal Question", ok1 and ok2 and ok3))
    except Exception as e:
        check("Legal question stream", False, str(e))
        results.append(("Legal Question", False))
else:
    print(f"  {INFO} Skipped — no conversation ID from TEST 2")
    results.append(("Legal Question", False))

# ── TEST 4: Non-legal question → refusal + no citations ───────────────────
print(f"\n{'─'*40}")
print("  TEST 4 — Non-Legal Question (expects refusal, no citations)")
print(f"{'─'*40}")
if conv_id:
    try:
        query = "What is the weather today?"
        print(f"  {INFO} Query : {query}")
        print(f"  {INFO} Streaming response:\n")
        print(f"  {SECTION}")
        text, citations = stream_message(conv_id, query)
        print(f"\n  {SECTION}")

        ok1 = check("Response received",       len(text) > 0)
        ok2 = check("Refusal message returned", "I can only assist with legal questions" in text)
        ok3 = check("No citations returned",    len(citations) == 0, f"got {len(citations)}")

        results.append(("Non-Legal Refusal", ok1 and ok2 and ok3))
    except Exception as e:
        check("Non-legal question stream", False, str(e))
        results.append(("Non-Legal Refusal", False))
else:
    print(f"  {INFO} Skipped — no conversation ID")
    results.append(("Non-Legal Refusal", False))

# ── TEST 5: Conversation persisted in DB ──────────────────────────────────
print(f"\n{'─'*40}")
print("  TEST 5 — Conversation Persisted in Database")
print(f"{'─'*40}")
if conv_id:
    try:
        data = http_get(f"/api/conversations/{conv_id}")
        messages = data.get("messages", [])
        ok1 = check("Conversation is retrievable", "id" in data)
        ok2 = check("Messages saved to DB",        len(messages) >= 2, f"{len(messages)} message(s)")
        roles = [m["role"] for m in messages]
        ok3 = check("Has user messages",      "user"      in roles)
        ok4 = check("Has assistant messages", "assistant" in roles)

        # Check citations persisted
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        all_citations = [c for m in assistant_msgs for c in m.get("citations", [])]
        ok5 = check("Citations persisted in DB", len(all_citations) > 0, f"{len(all_citations)} total citation(s)")

        results.append(("DB Persistence", ok1 and ok2 and ok3 and ok4))
    except Exception as e:
        check("Fetch conversation from DB", False, str(e))
        results.append(("DB Persistence", False))
else:
    results.append(("DB Persistence", False))

# ── TEST 6: List conversations ─────────────────────────────────────────────
print(f"\n{'─'*40}")
print("  TEST 6 — List All Conversations")
print(f"{'─'*40}")
try:
    data = http_get("/api/conversations")
    conversations = data if isinstance(data, list) else data.get("conversations", [])
    ok1 = check("Conversations list returned",      isinstance(conversations, list))
    ok2 = check("Test conversation appears in list", any(c.get("id") == conv_id for c in conversations))
    results.append(("List Conversations", ok1 and ok2))
except Exception as e:
    check("List conversations", False, str(e))
    results.append(("List Conversations", False))

# ── SUMMARY ────────────────────────────────────────────────────────────────
print(f"\n{DIVIDER}")
print("  TEST SUMMARY")
print(DIVIDER)
passed = sum(1 for _, ok in results if ok)
total  = len(results)
for name, ok in results:
    status = PASS if ok else FAIL
    print(f"  {status}  {name}")
print(DIVIDER)
print(f"  {passed}/{total} tests passed")
print(DIVIDER)

if passed < total:
    sys.exit(1)
