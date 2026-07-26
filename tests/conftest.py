"""Shared pytest fixtures."""

import sys
from io import BytesIO
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

# Add Backend to Python path so `app` imports work in tests
BACKEND_DIR = Path(__file__).resolve().parents[1] / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import create_app  # noqa: E402
from app.services.document_store import document_store  # noqa: E402


def make_sample_pdf(pages_text: list[str]) -> bytes:
    """Create a minimal in-memory PDF for tests."""
    document = fitz.open()
    for text in pages_text:
        page = document.new_page()
        page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    document_store.clear()
    return TestClient(create_app())


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Two-page PDF with extractable text."""
    return make_sample_pdf(
        [
            "Safety valve pressure rating is 150 PSI.",
            "Emergency shutdown procedure must be tested monthly.",
        ]
    )


@pytest.fixture
def blank_pdf_bytes() -> bytes:
    """PDF with a page but no extractable text."""
    return make_sample_pdf([""])
