"""Tests for text chunking and page metadata."""

import pytest

from app.models.document import PageContent
from app.services.text_chunker import chunk_document_pages


def test_short_page_produces_single_chunk() -> None:
    """A short page should become one chunk with correct metadata."""
    pages = [PageContent(page_number=1, text="Short safety note.")]

    chunks = chunk_document_pages(
        document_name="manual.pdf",
        pages=pages,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) == 1
    assert chunks[0].page_number == 1
    assert chunks[0].document_name == "manual.pdf"
    assert chunks[0].chunk_id == "manual.pdf-p1-c0"
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "Short safety note."


def test_long_page_splits_into_multiple_chunks() -> None:
    """Long page text should split while keeping the same page number."""
    long_text = "word " * 400  # ~2000 characters
    pages = [PageContent(page_number=3, text=long_text)]

    chunks = chunk_document_pages(
        document_name="report.pdf",
        pages=pages,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) > 1
    assert all(chunk.page_number == 3 for chunk in chunks)
    assert all(chunk.document_name == "report.pdf" for chunk in chunks)
    assert chunks[0].chunk_id == "report.pdf-p3-c0"
    assert chunks[1].chunk_id == "report.pdf-p3-c1"
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_multiple_pages_keep_page_metadata() -> None:
    """Each page should produce chunks tagged with its own page number."""
    pages = [
        PageContent(page_number=1, text="Page one content."),
        PageContent(page_number=2, text="Page two content."),
    ]

    chunks = chunk_document_pages(
        document_name="doc.pdf",
        pages=pages,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2
    assert "Page one" in chunks[0].text
    assert "Page two" in chunks[1].text


def test_empty_page_text_is_skipped() -> None:
    """Blank pages should not create empty chunks."""
    pages = [
        PageContent(page_number=1, text="   "),
        PageContent(page_number=2, text="Valid content here."),
    ]

    chunks = chunk_document_pages(
        document_name="doc.pdf",
        pages=pages,
        chunk_size=500,
        chunk_overlap=50,
    )

    assert len(chunks) == 1
    assert chunks[0].page_number == 2


def test_invalid_chunk_settings_raise_error() -> None:
    """Overlap must stay smaller than chunk size."""
    pages = [PageContent(page_number=1, text="Some text")]

    with pytest.raises(ValueError):
        chunk_document_pages(
            document_name="doc.pdf",
            pages=pages,
            chunk_size=100,
            chunk_overlap=100,
        )
