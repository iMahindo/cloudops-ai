from app.core.exceptions import RAGServiceException
from app.core.logging import get_logger
from app.schemas.rag import RAGResponse
from app.graphs.rag_graphs import rag_graph

logger = get_logger(__name__)

async def generate_rag_response(question: str) -> RAGResponse:
    if not question.strip():
        raise RAGServiceException(
            "Question cannot be empty"
        )
    try:
        result = await rag_graph.ainvoke(
            {
                "question": question
            }
        )

        if not result["is_valid"]:
            raise RAGServiceException(
                "The generated RAG response is invalid"
            )

        return RAGResponse(
            answer=result["answer"],
            #sources could be empty
            sources=result.get("sources", [])
        )
    except RAGServiceException:
        raise
    except Exception as exc:
        logger.exception("Failed to generate RAG response")
        raise RAGServiceException(
            "Failed to generate RAG response"
        ) from exc
