"""Document data structures used across extraction, chunking, and RAG."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageContent:
    """Extracted text from a single PDF page."""

    page_number: int
    text: str


@dataclass
class TextChunk:
    """A text segment ready for embedding and vector search."""

    chunk_id: str
    document_name: str
    page_number: int
    chunk_index: int
    text: str


@dataclass
class DocumentRecord:
    """Metadata and extracted content for an uploaded document."""

    document_name: str
    file_path: Path
    pages: list[PageContent] = field(default_factory=list)
    chunks: list[TextChunk] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def has_text(self) -> bool:
        return any(page.text.strip() for page in self.pages)
