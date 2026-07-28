"""In-memory store for the currently uploaded document (used by later phases)."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageContent:
    """Extracted text from a single PDF page."""

    page_number: int
    text: str


@dataclass
class DocumentRecord:
    """Metadata and extracted content for an uploaded document."""

    document_name: str
    file_path: Path
    pages: list[PageContent] = field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def has_text(self) -> bool:
        return any(page.text.strip() for page in self.pages)


class DocumentStore:
    """Simple store for the active document session."""

    def __init__(self) -> None:
        self._document: DocumentRecord | None = None

    @property
    def has_document(self) -> bool:
        return self._document is not None

    @property
    def current(self) -> DocumentRecord | None:
        return self._document

    def save(self, document: DocumentRecord) -> None:
        self._document = document

    def clear(self) -> None:
        self._document = None


# Shared instance used across request handlers and services
document_store = DocumentStore()
