"""Text chunking service for breaking documents into smaller pieces."""

from dataclasses import dataclass
from typing import List

from app.services.document_store import DocumentRecord

@dataclass
class DocumentChunk:
    """A text chunk with metadata."""
    text: str
    page_number: int
    chunk_index: int


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into chunks with a sliding window."""
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += (chunk_size - overlap)
        
    return chunks


def process_document_into_chunks(
    document: DocumentRecord, 
    chunk_size: int = 1000, 
    overlap: int = 200
) -> List[DocumentChunk]:
    """Process an entire document into chunks with page metadata."""
    all_chunks = []
    global_chunk_idx = 0
    
    for page in document.pages:
        text = page.text.strip()
        if not text:
            continue
            
        page_chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for chunk_text_content in page_chunks:
            all_chunks.append(
                DocumentChunk(
                    text=chunk_text_content,
                    page_number=page.page_number,
                    chunk_index=global_chunk_idx,
                )
            )
            global_chunk_idx += 1
            
    return all_chunks
