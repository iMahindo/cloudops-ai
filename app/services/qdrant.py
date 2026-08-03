from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)

def get_collections() -> list[str]:
    logger.info("Getting collections from Qdrant")
  
    try:
        response = client.get_collections()
        logger.info("Qdrant connection successful. Collections: %s")
    except Exception:
        logger.exception("Failed to connect to Qdrant")
        raise
    
    #translate to project structure
    collections_names = [collection.name for collection in response.collections]

    logger.info("Retrieved Qdrant collections: %s", len(collections_names))
    return collections_names