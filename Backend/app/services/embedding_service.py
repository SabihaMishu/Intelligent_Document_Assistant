"""Embedding and Vector Database service using ChromaDB and Gemini."""

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import chromadb.utils.embedding_functions as embedding_functions

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.services.chunking_service import DocumentChunk

logger = get_logger(__name__)


class VectorStoreService:
    """Service to handle vector database operations with Chroma."""
    
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        
        # Configure the embedding function to use Sentence Transformers
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
            
        self.collection_name = "document_chunks"

    def get_or_create_collection(self):
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

    def query_chunks(self, query: str, n_results: int = 5, document_name: str | None = None) -> list[dict]:
        """Query ChromaDB for relevant chunks."""
        collection = self.get_or_create_collection()
        
        where = {"document_name": document_name} if document_name else None
        
        # ChromaDB will call self.embedding_fn which uses Sentence Transformers.
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
        
        # Format results
        chunks = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return chunks


vector_store = VectorStoreService()
