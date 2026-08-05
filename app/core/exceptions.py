class LLMServiceException(Exception):
    """Raised when the LLM service cannot generate a response."""

class EmbeddingServiceException(Exception):
    """Raised when the embedding service cannot generate embeddings."""

class VectorDatabaseException(Exception):
    """Raised when the vector database cannot store or retrieve embeddings."""

class DocumentProcessingException(Exception):
    """Raised when document processing fails."""

class DocumentIngestionException(Exception):
    """Raised when document ingestion fails."""

class KnowledgeSearchException(Exception):
    """Raised when knoledge search fails."""    