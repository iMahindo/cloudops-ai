from time import perf_counter

from app.core.exceptions import RAGServiceException
from app.core.logging import get_logger
from app.graphs.rag_graphs import rag_graph
from app.observability.metrics import (
    RAG_DURATION_SECONDS,
    RAG_EXECUTIONS_TOTAL,
    RAG_FAILURES_TOTAL,
)
from app.schemas.rag import RAGResponse

logger = get_logger(__name__)

async def generate_rag_response(question: str) -> RAGResponse:
    if not question.strip():
        raise RAGServiceException(
            "Question cannot be empty"
        )

    #start time and inc executions
    start_time = perf_counter()
    RAG_EXECUTIONS_TOTAL.inc()
    
    try:
        #invoke the graph
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
        #Update the failure metrics
        RAG_FAILURES_TOTAL.inc()
        raise
    except Exception as exc:
        logger.exception("Failed to generate RAG response")

        #Update the failure metrics
        RAG_FAILURES_TOTAL.inc()

        raise RAGServiceException(
            "Failed to generate RAG response"
        ) from exc

    finally:
        RAG_DURATION_SECONDS.observe(perf_counter() - start_time)