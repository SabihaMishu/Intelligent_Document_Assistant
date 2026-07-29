"""Embedding and Vector Database service using ChromaDB and Gemini."""

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.services.chunking_service import DocumentChunk

logger = get_logger(__name__)


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function for ChromaDB using Google Gemini."""
    
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        if not api_key:
            raise AppError("Gemini API key is missing. Set GEMINI_API_KEY.", status_code=500)
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        """Generate embeddings for a list of documents."""
        # Using task_type="RETRIEVAL_DOCUMENT" for documents in the database
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=input,
                task_type="RETRIEVAL_DOCUMENT",
            )
            # embed_content returns a dictionary with 'embedding' key which is a list of embeddings
            return result['embedding']
        except Exception as e:
            logger.error("Error generating embeddings: %s", e)
            raise AppError(f"Failed to generate embeddings: {e}", status_code=500)


class VectorStoreService:
    """Service to handle vector database operations with Chroma."""
    
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        
        # Configure the embedding function
        api_key = settings.gemini_api_key
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set. Vector store might not work if embeddings are requested.")
            self.embedding_fn = None
        else:
            self.embedding_fn = GeminiEmbeddingFunction(api_key=api_key)
            
        self.collection_name = "document_chunks"

    def get_or_create_collection(self):
        if not self.embedding_fn:
             raise AppError("Gemini API key is not configured.", status_code=500)
             
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
        )

    def store_chunks(self, document_name: str, chunks: list[DocumentChunk]) -> int:
        """Store document chunks and their embeddings in ChromaDB."""
        if not chunks:
            return 0
            
        collection = self.get_or_create_collection()
        
        # We need to format the data for ChromaDB
        ids = [f"{document_name}_chunk_{c.chunk_index}" for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [{"page_number": c.page_number, "document_name": document_name} for c in chunks]
        
        # Add to collection (Chroma will automatically compute embeddings using the embedding function)
        # Note: We process in batches if there are many chunks to avoid hitting API limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )
            logger.info("Stored batch of %d chunks to ChromaDB", len(ids[i:i + batch_size]))
            
        return len(ids)

    def clear_collection(self):
        """Clear the entire collection (useful for testing or resetting)."""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass

vector_store = VectorStoreService()
