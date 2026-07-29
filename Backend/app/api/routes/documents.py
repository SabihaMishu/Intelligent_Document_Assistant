"""Document upload endpoints."""

from fastapi import APIRouter, File, UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.schemas import DocumentUploadResponse, DocumentProcessResponse
from app.services.document_service import process_pdf_upload
from app.services.document_store import document_store
from app.services.chunking_service import process_document_into_chunks
from app.services.embedding_service import vector_store

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload a PDF document",
    description=(
        "Upload a PDF file, validate it, extract text from each page, "
        "and store page metadata for later RAG processing."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
) -> DocumentUploadResponse:
    """Accept a PDF upload and extract page-level text."""
    if file.content_type and file.content_type not in {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }:
        raise AppError(
            "Invalid file type. Only PDF files are accepted.",
            status_code=400,
        )

    content = await file.read()
    settings = get_settings()
    record = process_pdf_upload(
        content=content,
        filename=file.filename or "",
        settings=settings,
    )

    return DocumentUploadResponse(
        document_name=record.document_name,
        page_count=record.page_count,
        message="Document uploaded and text extracted successfully.",
    )


@router.post(
    "/process",
    response_model=DocumentProcessResponse,
    summary="Chunk and embed the uploaded document",
    description="Chunk the text of the previously uploaded document and store embeddings in ChromaDB.",
)
async def process_document() -> DocumentProcessResponse:
    """Process the current document: chunk text and store embeddings."""
    if not document_store.has_document or not document_store.current:
        raise AppError("No active document found. Please upload a PDF first.", status_code=400)
        
    doc = document_store.current
    
    # 1. Chunking
    chunks = process_document_into_chunks(doc)
    if not chunks:
        raise AppError("No text could be extracted or chunked from the document.", status_code=400)
        
    # 2. Embeddings & Vector Store
    chunks_stored = vector_store.store_chunks(document_name=doc.document_name, chunks=chunks)
    
    return DocumentProcessResponse(
        document_name=doc.document_name,
        chunks_created=chunks_stored,
        message="Document chunks embedded and stored in ChromaDB successfully.",
    )

