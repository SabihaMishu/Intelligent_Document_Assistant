"""Shared API schemas (request and response models)."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str = Field(..., examples=["healthy"])
    service: str = Field(..., examples=["AI Engineering Document Assistant"])
    version: str = Field(..., examples=["0.1.0"])
    environment: str = Field(..., examples=["development"])


class DocumentUploadResponse(BaseModel):
    """Response model after a successful PDF upload."""

    document_name: str = Field(..., examples=["engineering_manual.pdf"])
    page_count: int = Field(..., ge=1, examples=[12])
    chunk_count: int = Field(..., ge=1, examples=[28])
    message: str = Field(
        ...,
        examples=["Document uploaded, text extracted, and chunked successfully."],
    )
