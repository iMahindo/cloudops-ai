import pytest

from app.core.exceptions import RAGServiceException
from app.schemas.rag import RAGSource
from app.services import rag


@pytest.mark.asyncio
async def test_generate_rag_response_rejects_empty_question() -> None:
    with pytest.raises(
        RAGServiceException,
        match="Question cannot be empty",
    ):
        await rag.generate_rag_response("   ")


@pytest.mark.asyncio
async def test_generate_rag_response_returns_answer_and_sources(monkeypatch) -> None:
    class FakeRAGGraph:
        async def ainvoke(self, payload):
            assert payload == {
                "question": "How do I configure VPC peering?"
            }

            return {
                "answer": "Generated RAG answer",
                "sources": [
                    RAGSource(
                        file_name="networking.md",
                        chunk_index=0,
                    ),
                    RAGSource(
                        file_name="k8s.md",
                        chunk_index=2,
                    ),
                ],
                "is_valid": True,
            }

    monkeypatch.setattr(
        rag,
        "rag_graph",
        FakeRAGGraph(),
    )

    response = await rag.generate_rag_response(
        "How do I configure VPC peering?"
    )

    assert response.answer == "Generated RAG answer"
    assert len(response.sources) == 2
    assert response.sources[0].file_name == "networking.md"
    assert response.sources[0].chunk_index == 0
    assert response.sources[1].file_name == "k8s.md"
    assert response.sources[1].chunk_index == 2


@pytest.mark.asyncio
async def test_generate_rag_response_returns_empty_sources_for_direct_answer(monkeypatch) -> None:
    class FakeRAGGraph:
        async def ainvoke(self, payload):
            return {
                "answer": "HTTP 500 means Internal Server Error.",
                "is_valid": True,
            }

    monkeypatch.setattr(
        rag,
        "rag_graph",
        FakeRAGGraph(),
    )

    response = await rag.generate_rag_response(
        "What does HTTP 500 mean?"
    )

    assert response.answer == "HTTP 500 means Internal Server Error."
    assert response.sources == []


@pytest.mark.asyncio
async def test_generate_rag_response_raises_when_graph_result_is_invalid(monkeypatch) -> None:
    class FakeRAGGraph:
        async def ainvoke(self, payload):
            return {
                "answer": "",
                "is_valid": False,
            }

    monkeypatch.setattr(
        rag,
        "rag_graph",
        FakeRAGGraph(),
    )

    with pytest.raises(
        RAGServiceException,
        match="The generated RAG response is invalid",
    ):
        await rag.generate_rag_response("What is CloudOps?")


@pytest.mark.asyncio
async def test_generate_rag_response_wraps_unexpected_graph_failure(monkeypatch) -> None:
    class FailingRAGGraph:
        async def ainvoke(self, payload):
            raise RuntimeError("Graph execution failed")

    monkeypatch.setattr(
        rag,
        "rag_graph",
        FailingRAGGraph(),
    )

    with pytest.raises(
        RAGServiceException,
        match="Failed to generate RAG response",
    ):
        await rag.generate_rag_response("What is CloudOps?")