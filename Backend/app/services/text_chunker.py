"""Text chunking with page-level metadata preservation."""

from app.core.logging import get_logger
from app.models.document import PageContent, TextChunk

logger = get_logger(__name__)


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split long page text into overlapping chunks at word boundaries when possible."""
    cleaned = text.strip()
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))

        if end < len(cleaned):
            window = cleaned[start:end]
            last_space = window.rfind(" ")
            if last_space > chunk_size // 2:
                end = start + last_space

        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= len(cleaned):
            break

        next_start = end - chunk_overlap
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def _make_chunk_id(document_name: str, page_number: int, local_index: int) -> str:
    """Build a stable, human-readable chunk identifier."""
    safe_name = document_name.replace(" ", "_")
    return f"{safe_name}-p{page_number}-c{local_index}"


def chunk_document_pages(
    document_name: str,
    pages: list[PageContent],
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    """
    Split extracted pages into chunks while preserving page metadata.

    Each chunk keeps the page number it came from. Long pages are split into
    multiple chunks; short pages may produce a single chunk.
    """
    chunks: list[TextChunk] = []
    global_index = 0

    for page in pages:
        page_parts = _split_text(page.text, chunk_size, chunk_overlap)
        for local_index, part in enumerate(page_parts):
            chunk = TextChunk(
                chunk_id=_make_chunk_id(document_name, page.page_number, local_index),
                document_name=document_name,
                page_number=page.page_number,
                chunk_index=global_index,
                text=part,
            )
            chunks.append(chunk)
            global_index += 1

    logger.info(
        "Created %s chunk(s) from %s page(s) for '%s'",
        len(chunks),
        len(pages),
        document_name,
    )
    return chunks
