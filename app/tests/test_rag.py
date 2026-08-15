import pytest
from types import SimpleNamespace

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
                        name="networking.md",
                        chunk_index=0,
                    ),
                    RAGSource(
                        name="k8s.md",
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
    assert response.sources[0].name == "networking.md"
    assert response.sources[0].chunk_index == 0
    assert response.sources[1].name == "k8s.md"
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

@pytest.mark.asyncio
async def test_generate_rag_response_updates_metrics_on_success(monkeypatch):
    calls = SimpleNamespace(
        executions=0,
        failures=0,
        duration=0,
    )

    monkeypatch.setattr(
        rag,
        "RAG_EXECUTIONS_TOTAL",
        SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "executions",
                calls.executions + 1,
            )
        ),
    )

    monkeypatch.setattr(
        rag,
        "RAG_FAILURES_TOTAL",
        SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "failures",
                calls.failures + 1,
            )
        ),
    )

    monkeypatch.setattr(
        rag,
        "RAG_DURATION_SECONDS",
        SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        ),
    )

    class FakeRAGGraph:
        async def ainvoke(self, payload):
            return {
                "answer": "OK",
                "sources": [],
                "is_valid": True,
            }

    monkeypatch.setattr(rag, "rag_graph", FakeRAGGraph())

    await rag.generate_rag_response("Question")

    assert calls.executions == 1
    assert calls.failures == 0
    assert calls.duration == 1

@pytest.mark.asyncio
async def test_generate_rag_response_updates_metrics_on_failure(monkeypatch):
    calls = SimpleNamespace(
        executions=0,
        failures=0,
        duration=0,
    )

    monkeypatch.setattr(
        rag,
        "RAG_EXECUTIONS_TOTAL",
        SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "executions",
                calls.executions + 1,
            )
        ),
    )

    monkeypatch.setattr(
        rag,
        "RAG_FAILURES_TOTAL",
        SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "failures",
                calls.failures + 1,
            )
        ),
    )

    monkeypatch.setattr(
        rag,
        "RAG_DURATION_SECONDS",
        SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        ),
    )

    class FailingRAGGraph:
        async def ainvoke(self, payload):
            raise RuntimeError("boom")

    monkeypatch.setattr(rag, "rag_graph", FailingRAGGraph())

    with pytest.raises(RAGServiceException):
        await rag.generate_rag_response("Question")

    assert calls.executions == 1
    assert calls.failures == 1
    assert calls.duration == 1