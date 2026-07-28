"""Document upload endpoints."""

from fastapi import APIRouter, File, UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.schemas import DocumentUploadResponse
from app.services.document_service import process_pdf_upload

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
