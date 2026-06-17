import io

import pytest
from httpx import AsyncClient


def _make_pdf_bytes() -> bytes:
    # Minimal valid PDF structure
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n" \
           b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n" \
           b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\n" \
           b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n" \
           b"0000000058 00000 n\n0000000115 00000 n\n" \
           b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient):
    response = await client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient):
    pdf_bytes = _make_pdf_bytes()
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("test_contract.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_contract.pdf"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_documents_after_upload(client: AsyncClient):
    pdf_bytes = _make_pdf_bytes()
    await client.post(
        "/api/documents/upload",
        files={"file": ("doc1.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    await client.post(
        "/api/documents/upload",
        files={"file": ("doc2.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    response = await client.get("/api/documents")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_document(client: AsyncClient):
    pdf_bytes = _make_pdf_bytes()
    upload_resp = await client.post(
        "/api/documents/upload",
        files={"file": ("contract.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    doc_id = upload_resp.json()["id"]

    response = await client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


@pytest.mark.asyncio
async def test_get_document_not_found(client: AsyncClient):
    response = await client.get("/api/documents/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient):
    pdf_bytes = _make_pdf_bytes()
    upload_resp = await client.post(
        "/api/documents/upload",
        files={"file": ("to_delete.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    doc_id = upload_resp.json()["id"]

    del_resp = await client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/documents/{doc_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_non_pdf_rejected(client: AsyncClient):
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("document.txt", io.BytesIO(b"hello world"), "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_document_not_found(client: AsyncClient):
    response = await client.delete("/api/documents/bad-id")
    assert response.status_code == 404
