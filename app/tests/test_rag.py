import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.core.config import settings
from app.core.exceptions import RAGServiceException
from app.schemas.knowledge_search import KnowledgeSearchResponse, KnowledgeSearchResult
from app.services import rag


@pytest.mark.asyncio
async def test_generate_rag_response_rejects_empty_question() -> None:
    with pytest.raises(RAGServiceException, match="Question cannot be empty"):
        await rag.generate_rag_response("   ")


@pytest.mark.asyncio
async def test_generate_rag_response_returns_answer_and_sources(monkeypatch) -> None:
    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        return KnowledgeSearchResponse(
            results=[
                KnowledgeSearchResult(
                    content="How to configure VPC peering",
                    metadata={"file_name": "networking.md", "chunk_index": 0},
                ),
                KnowledgeSearchResult(
                    content="Kubernetes ingress troubleshooting",
                    metadata={"file_name": "k8s.md", "chunk_index": 2},
                ),
            ]
        )

    monkeypatch.setattr(
        rag,
        "search_knowledge",
        mock_search_knowledge,
    )
    monkeypatch.setattr(
        rag,
        "llm",
        FakeListChatModel(responses=["Generated RAG answer"]),
    )

    response = await rag.generate_rag_response("How do I configure VPC peering?")

    assert response.answer == "Generated RAG answer"
    assert len(response.sources) == 2
    assert response.sources[0].file_name == "networking.md"
    assert response.sources[0].chunk_index == 0
    assert response.sources[1].file_name == "k8s.md"
    assert response.sources[1].chunk_index == 2


@pytest.mark.asyncio
async def test_generate_rag_response_passes_question_and_limit_to_search(monkeypatch) -> None:
    captured_arguments = {}

    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        captured_arguments["query"] = query
        captured_arguments["limit"] = limit
        return KnowledgeSearchResponse(results=[])

    monkeypatch.setattr(
        rag,
        "search_knowledge",
        mock_search_knowledge,
    )
    monkeypatch.setattr(
        rag,
        "llm",
        FakeListChatModel(responses=["Answer without context"]),
    )

    await rag.generate_rag_response("What is CloudOps?")

    assert captured_arguments == {
        "query": "What is CloudOps?",
        "limit": settings.rag_retrieval_limit,
    }


@pytest.mark.asyncio
async def test_generate_rag_response_raises_rag_service_exception_when_search_fails(
    monkeypatch,
) -> None:
    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        raise RuntimeError("Knowledge search failed")

    monkeypatch.setattr(
        rag,
        "search_knowledge",
        mock_search_knowledge,
    )

    with pytest.raises(
        RAGServiceException,
        match="Failed to generate RAG response",
    ):
        await rag.generate_rag_response("What is CloudOps?")


@pytest.mark.asyncio
async def test_generate_rag_response_raises_rag_service_exception_when_llm_fails(
    monkeypatch,
) -> None:
    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        return KnowledgeSearchResponse(
            results=[
                KnowledgeSearchResult(
                    content="Some context",
                    metadata={"file_name": "guide.md", "chunk_index": 1},
                )
            ]
        )

    class FailingLLM(FakeListChatModel):
        async def ainvoke(self, *args, **kwargs):
            raise RuntimeError("LLM provider unavailable")

    monkeypatch.setattr(
        rag,
        "search_knowledge",
        mock_search_knowledge,
    )
    monkeypatch.setattr(
        rag,
        "llm",
        FailingLLM(responses=[]),
    )

    with pytest.raises(
        RAGServiceException,
        match="Failed to generate RAG response",
    ):
        await rag.generate_rag_response("What is CloudOps?")
