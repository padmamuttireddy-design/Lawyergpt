import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_conversations_empty(client: AsyncClient):
    response = await client.get("/api/conversations")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient):
    response = await client.post("/api/conversations")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "New Chat"
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_list_conversations_after_create(client: AsyncClient):
    await client.post("/api/conversations")
    await client.post("/api/conversations")
    response = await client.get("/api/conversations")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    response = await client.get(f"/api/conversations/{conv_id}")
    assert response.status_code == 200
    assert response.json()["id"] == conv_id


@pytest.mark.asyncio
async def test_get_conversation_not_found(client: AsyncClient):
    response = await client.get("/api/conversations/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/conversations/{conv_id}",
        json={"title": "Contract Review"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Contract Review"


@pytest.mark.asyncio
async def test_rename_conversation_not_found(client: AsyncClient):
    response = await client.patch(
        "/api/conversations/bad-id",
        json={"title": "Whatever"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient):
    create_resp = await client.post("/api/conversations")
    conv_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/conversations/{conv_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/conversations/{conv_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation_not_found(client: AsyncClient):
    response = await client.delete("/api/conversations/bad-id")
    assert response.status_code == 404
