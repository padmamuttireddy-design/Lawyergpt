import json

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_message_streams(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"role": "user", "content": "What is contract law?", "model": "gpt-5.5"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    body = response.text
    lines = [l for l in body.split("\n") if l.startswith("data: ")]
    assert len(lines) >= 2

    events = [json.loads(l[6:]) for l in lines if l[6:].strip()]
    event_types = [e["type"] for e in events]
    assert "token" in event_types
    assert "citations" in event_types
    assert "done" in event_types

    done_event = next(e for e in events if e["type"] == "done")
    assert done_event["message"]["role"] == "assistant"
    assert done_event["message"]["conversation_id"] == conv_id


@pytest.mark.asyncio
async def test_send_message_conversation_not_found(client: AsyncClient):
    response = await client.post(
        "/api/conversations/bad-id/messages",
        json={"role": "user", "content": "Hello", "model": "gpt-5.5"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_persists_in_history(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    await client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"role": "user", "content": "Tell me about IP law", "model": "gpt-4o"},
    )

    get_resp = await client.get(f"/api/conversations/{conv_id}")
    messages = get_resp.json()["messages"]
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles


@pytest.mark.asyncio
async def test_send_message_user_content_in_response(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    user_text = "What are the penalties for breach of contract?"
    await client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"role": "user", "content": user_text, "model": "gpt-5.5"},
    )

    get_resp = await client.get(f"/api/conversations/{conv_id}")
    messages = get_resp.json()["messages"]
    user_messages = [m for m in messages if m["role"] == "user"]
    assert any(user_text in m["content"] for m in user_messages)
