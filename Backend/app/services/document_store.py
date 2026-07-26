"""In-memory store for the currently uploaded document (used by later phases)."""

from app.models.document import DocumentRecord


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
