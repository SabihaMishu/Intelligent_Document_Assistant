"""PDF text extraction using PyMuPDF with page-level metadata."""

import fitz

from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.services.document_store import PageContent

logger = get_logger(__name__)

PDF_MAGIC_BYTES = b"%PDF"


def validate_pdf_bytes(content: bytes, max_size_bytes: int) -> None:
    """Validate raw upload bytes before extraction."""
    if not content:
        raise AppError("The uploaded file is empty.", status_code=400)

    if len(content) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise AppError(
            f"File is too large. Maximum allowed size is {max_mb:.0f} MB.",
            status_code=413,
        )

    if not content.startswith(PDF_MAGIC_BYTES):
        raise AppError(
            "Invalid file type. Only valid PDF files are accepted.",
            status_code=400,
        )


def extract_text_from_pdf(content: bytes) -> list[PageContent]:
    """
    Extract text from each page of a PDF.

    Page numbers are 1-based to match how users see PDF page labels.
    """
    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        logger.warning("Failed to open PDF: %s", exc)
        raise AppError(
            "The file could not be read as a valid PDF.",
            status_code=400,
        ) from exc

    try:
        if document.page_count == 0:
            raise AppError("The PDF has no pages.", status_code=400)

        pages: list[PageContent] = []
        for index in range(document.page_count):
            page = document.load_page(index)
            text = page.get_text("text").strip()
            pages.append(PageContent(page_number=index + 1, text=text))

        if not any(page.text for page in pages):
            raise AppError(
                "No extractable text was found in the PDF. "
                "Image-only or scanned PDFs are not supported yet.",
                status_code=400,
            )

        logger.info("Extracted text from %s page(s)", len(pages))
        return pages
    finally:
        document.close()
