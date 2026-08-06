from app.core.logging import get_logger
from app.core.exceptions import KnowledgeSearchException
from app.schemas.knowledge_search import KnowledgeSearchResult, KnowledgeSearchResponse
from app.services.qdrant import get_vector_store


logger = get_logger(__name__)

async def search_knowledge(query: str,limit: int) -> KnowledgeSearchResponse:
    if not query.strip():
        raise KnowledgeSearchException(
            "Search query cannot be empty"
        )

    if limit < 1:
        raise KnowledgeSearchException(
            "Search limit must be greater than zero"
        )

    try:
        vector_store = get_vector_store()

        documents = await vector_store.asimilarity_search(query=query, k=limit)

        results = []
        for document in documents:
            result = KnowledgeSearchResult(content = document.page_content, metadata = document.metadata)
            results.append(result)
        
        return KnowledgeSearchResponse(results = results)
    except Exception as exc:
        logger.exception(
            "Failed to search knowledge base"
        )
        raise KnowledgeSearchException(
            "Failed to search knowledge base"
        ) from exc

