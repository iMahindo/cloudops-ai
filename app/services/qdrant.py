from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import VectorDatabaseException
from app.services.embeddings import embedding_model

logger = get_logger(__name__)

client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)

#Get the collections stored
def get_collections() -> list[str]:
    logger.info("Getting collections from Qdrant")
  
    try:
        response = client.get_collections()
        logger.info("Qdrant connection successful. Collections")
    except Exception as exc:
        logger.exception("Failed to connect to Qdrant")
        raise VectorDatabaseException(
            "Failed to ensure vector collection"
        ) from exc
    
    #translate to project structure
    collections_names = [collection.name for collection in response.collections]

    logger.info("Retrieved Qdrant collections: %s", len(collections_names))
    return collections_names

#Create a new collection
def create_knowledge_collection() -> None:
    try:
        # Check if the collection exists
        collection_exists = client.collection_exists(
            collection_name=settings.qdrant_collection,
        )
        
        if collection_exists:
            logger.info(
                "Qdrant collection %s already exists",
                settings.qdrant_collection,
            )
            return
        
        vector_config = VectorParams(
            size = settings.gemini_embedding_dimension,
            distance = Distance.COSINE
        )
    
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=vector_config,
        )
    except Exception as exc:
        logger.exception("Error creating the collection %s", settings.qdrant_collection)
        raise VectorDatabaseException(
            "Failed to ensure vector collection"
        ) from exc

def get_vector_store() -> QdrantVectorStore:
    try:
        logger.info(
            "Creating Qdrant vector store for collection %s",
            settings.qdrant_collection,
        )

        return QdrantVectorStore(
            client=client,
            collection_name=settings.qdrant_collection,
            embedding=embedding_model,
        )

    except Exception as exc:
        logger.exception(
            "Failed creating Qdrant vector store"
        )
        raise VectorDatabaseException(
            "Failed creating Qdrant vector store"
        ) from exc