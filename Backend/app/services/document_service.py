"""Document upload workflow: validate, save, extract, and store."""

import re
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.models.document import DocumentRecord
from app.services.document_store import document_store
from app.services.pdf_extractor import extract_text_from_pdf, validate_pdf_bytes
from app.services.text_chunker import chunk_document_pages

logger = get_logger(__name__)


def _sanitize_filename(filename: str) -> str:
    """Keep only the basename and replace unsafe characters."""
    clean_name = Path(filename).name.strip()
    if not clean_name:
        raise AppError("A valid file name is required.", status_code=400)

    clean_name = re.sub(r"[^\w.\- ]", "_", clean_name)
    if not clean_name.lower().endswith(".pdf"):
        raise AppError(
            "Invalid file type. Only PDF files with a .pdf extension are accepted.",
            status_code=400,
        )
    return clean_name


def process_pdf_upload(content: bytes, filename: str, settings: Settings) -> DocumentRecord:
    """
    Validate an uploaded PDF, save it locally, extract text, and store metadata.

    Returns the document record for API responses and later RAG phases.
    """
    if not filename:
        raise AppError("No file was uploaded.", status_code=400)

    safe_name = _sanitize_filename(filename)
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    validate_pdf_bytes(content, max_size_bytes=max_size_bytes)
    pages = extract_text_from_pdf(content)
    chunks = chunk_document_pages(
        document_name=safe_name,
        pages=pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.uploads_dir / safe_name
    file_path.write_bytes(content)

    record = DocumentRecord(
        document_name=safe_name,
        file_path=file_path,
        pages=pages,
        chunks=chunks,
    )
    document_store.save(record)

    logger.info(
        "Stored document '%s' with %s page(s) and %s chunk(s) at %s",
        record.document_name,
        record.page_count,
        record.chunk_count,
        file_path,
    )
    return record
