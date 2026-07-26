"""Tests for PDF upload and text extraction."""

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import AppError
from app.services.document_store import document_store
from app.services.pdf_extractor import extract_text_from_pdf
from tests.conftest import make_sample_pdf


def test_upload_valid_pdf(client: TestClient, sample_pdf_bytes: bytes) -> None:
    """Valid PDF upload should return metadata and store extracted pages."""
    response = client.post(
        "/documents/upload",
        files={"file": ("manual.pdf", sample_pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["document_name"] == "manual.pdf"
    assert data["page_count"] == 2
    assert data["chunk_count"] >= 2
    assert "successfully" in data["message"].lower()

    record = document_store.current
    assert record is not None
    assert record.page_count == 2
    assert record.chunk_count >= 2
    assert record.pages[0].page_number == 1
    assert "Safety valve" in record.pages[0].text
    assert all(chunk.document_name == "manual.pdf" for chunk in record.chunks)
    assert {chunk.page_number for chunk in record.chunks} == {1, 2}


def test_upload_invalid_pdf_extension(client: TestClient) -> None:
    """Non-PDF files should be rejected."""
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert "pdf" in response.json()["detail"].lower()


def test_upload_invalid_pdf_content(client: TestClient) -> None:
    """A .pdf file with invalid content should be rejected."""
    response = client.post(
        "/documents/upload",
        files={"file": ("broken.pdf", b"not-a-real-pdf", "application/pdf")},
    )

    assert response.status_code == 400
    assert "invalid file type" in response.json()["detail"].lower()


def test_upload_empty_file(client: TestClient) -> None:
    """Empty uploads should be rejected."""
    response = client.post(
        "/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_extract_text_from_pdf(sample_pdf_bytes: bytes) -> None:
    """Extractor should return page numbers and text content."""
    pages = extract_text_from_pdf(sample_pdf_bytes)

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[1].page_number == 2
    assert "Safety valve" in pages[0].text
    assert "Emergency shutdown" in pages[1].text


def test_extract_text_rejects_blank_pdf(blank_pdf_bytes: bytes) -> None:
    """PDFs with no extractable text should raise a clear error."""
    with pytest.raises(AppError) as exc_info:
        extract_text_from_pdf(blank_pdf_bytes)

    assert "no extractable text" in exc_info.value.message.lower()


def test_make_sample_pdf_helper() -> None:
    """Test helper should produce readable multi-page PDF bytes."""
    pdf_bytes = make_sample_pdf(["Page one", "Page two"])
    pages = extract_text_from_pdf(pdf_bytes)
    assert len(pages) == 2
