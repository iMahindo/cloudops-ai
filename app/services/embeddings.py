from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings
from app.core.exceptions import EmbeddingServiceException
from app.core.logging import get_logger

logger = get_logger(__name__)

embedding_model = GoogleGenerativeAIEmbeddings(
    model=settings.gemini_embedding_model,
    google_api_key=settings.gemini_api_key,
    output_dimensionality=settings.gemini_embedding_dimension,
)

def generate_document_embeddings(texts: list[str]) -> list[list[float]]:
    try:
        if not texts:
            raise ValueError("Texts cannot be empty")

        if any(not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty values")

        logger.info(
            "Generating embeddings for %s documents using model %s",
            len(texts),
            settings.gemini_embedding_model,
        )

        return embedding_model.embed_documents(texts)

    except Exception as exc:
        logger.exception("Failed to generate document embeddings")
        raise EmbeddingServiceException(
            "Failed to generate document embeddings"
    ) from exc

def generate_query_embedding(text: str) -> list[float]:
    try:
        if not text.strip():
            raise ValueError("Text cannot be empty")

        logger.info(
            "Generating query embedding using model %s",
            settings.gemini_embedding_model,
        )

        return embedding_model.embed_query(text)

    except Exception as exc:
        logger.exception("Failed to generate query embedding")
        raise EmbeddingServiceException(
            "Failed to generate query embedding"
    ) from exc