# AI Engineering Document Assistant

A portfolio-ready AI SaaS-style application for uploading engineering PDF documents, asking grounded questions with RAG, and running risk/compliance analysis.

## Architecture (Phase 1)

```
Document Assistant/
├── Backend/                 # FastAPI backend API
│   └── app/
│       ├── main.py          # App entry point
│       ├── api/routes/      # HTTP endpoints
│       ├── core/            # Config, logging
│       ├── models/          # Pydantic schemas
│       └── services/        # Business logic (later phases)
├── Frontend/                # Streamlit UI (Phase 9)
├── tests/                   # pytest test suite
├── Data/
│   ├── uploads/             # Uploaded PDFs (local, gitignored)
│   └── chroma/              # ChromaDB storage (Phase 4)
├── .env.example             # Environment variable template
└── requirements.txt         # Python dependencies
```

## Prerequisites

- Python 3.11 or newer
- pip

## Setup (Phase 1)

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

   **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**

   ```bash
   source .venv/bin/activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional for Phase 1)**

   ```bash
   copy .env.example .env
   ```

   Phase 1 does not require `GEMINI_API_KEY` yet.

## Run the backend

From the project root, with the virtual environment activated:

```bash
cd Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test the API

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

Expected health response:

```json
{
  "status": "healthy",
  "service": "AI Engineering Document Assistant",
  "version": "0.1.0",
  "environment": "development"
}
```

### Upload a PDF (Phase 2)

In Swagger UI (`/docs`), open **POST /documents/upload**, choose a PDF file, and execute.

Expected success response:

```json
{
  "document_name": "your_file.pdf",
  "page_count": 5,
  "chunk_count": 12,
  "message": "Document uploaded, text extracted, and chunked successfully."
}
```

The PDF is saved under `Data/uploads/`. Extracted pages and text chunks (with page metadata) are kept in memory for later embedding and RAG phases.

**PowerShell example:**

```powershell
curl.exe -X POST "http://localhost:8000/documents/upload" `
  -F "file=@C:\path\to\your\document.pdf;type=application/pdf"
```

## Run tests

From the project root:

```bash
pytest tests/ -v
```

## Development phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Done | Project structure + FastAPI + `/health` |
| 2 | ✅ Done | PDF upload and text extraction |
| 3 | ✅ Current | Chunking and page metadata |
| 4 | Pending | Embeddings and ChromaDB |
| 5 | Pending | RAG question answering |
| 6 | Pending | Source citation |
| 7 | Pending | Answer verification |
| 8 | Pending | Risk analysis |
| 9 | Pending | Streamlit frontend |
| 10 | Pending | Tests, error handling, logging |
| 11 | Pending | Final README and GitHub config |
