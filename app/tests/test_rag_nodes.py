from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.graphs.rag_nodes import (
    classify_question,
    generate_answer,
    retrieve_context,
    route_question,
    validate_answer,
)
from app.schemas.rag import RAGQuestionClassification, RAGSource


def test_route_question_returns_retrieval_when_required():
    state = {
        "question": "test",
        "requires_retrieval": True,
    }

    result = route_question(state)

    assert result == "retrieval"


def test_route_question_returns_direct_when_retrieval_not_required():
    state = {
        "question": "test",
        "requires_retrieval": False,
    }

    result = route_question(state)

    assert result == "direct"

def test_validate_answer_returns_false_when_answer_is_empty():
    state = {
        "question": "test",
        "requires_retrieval": False,
        "answer": "   ",
    }

    result = validate_answer(state)

    assert result == {
        "is_valid": False
    }


def test_validate_answer_returns_false_when_retrieval_context_is_empty():
    state = {
        "question": "test",
        "requires_retrieval": True,
        "context": "   ",
        "answer": "Some answer",
    }

    result = validate_answer(state)

    assert result == {
        "is_valid": False
    }


def test_validate_answer_returns_true_for_valid_answer():
    state = {
        "question": "test",
        "requires_retrieval": True,
        "context": "Relevant internal knowledge",
        "answer": "Valid answer",
    }

    result = validate_answer(state)

    assert result == {
        "is_valid": True
    }

@pytest.mark.asyncio
async def test_retrieve_context_builds_context_and_sources(monkeypatch):
    async def fake_search_knowledge(query: str, limit: int):
        return SimpleNamespace(
            results=[
                SimpleNamespace(
                    content="First chunk",
                    metadata={
                        "file_name": "runbook.md",
                        "chunk_index": 0,
                    },
                ),
                SimpleNamespace(
                    content="Second chunk",
                    metadata={
                        "file_name": "runbook.md",
                        "chunk_index": 1,
                    },
                ),
            ]
        )

    monkeypatch.setattr(
        "app.graphs.rag_nodes.search_knowledge",
        fake_search_knowledge,
    )

    state = {
        "question": "How do I restart the service?",
        "requires_retrieval": True,
    }

    result = await retrieve_context(state)

    assert result["context"] == "First chunk\n\nSecond chunk"
    assert result["sources"] == [
        RAGSource(
            name="runbook.md",
            chunk_index=0,
        ),
        RAGSource(
            name="runbook.md",
            chunk_index=1,
        ),
    ]

@pytest.mark.asyncio
async def test_retrieve_context_uses_question_and_configured_limit(monkeypatch):
    captured = {}

    async def fake_search_knowledge(query: str, limit: int):
        captured["query"] = query
        captured["limit"] = limit

        return SimpleNamespace(
            results=[]
        )

    monkeypatch.setattr(
        "app.graphs.rag_nodes.search_knowledge",
        fake_search_knowledge,
    )

    state = {
        "question": "How do I restart the service?",
        "requires_retrieval": True,
    }

    await retrieve_context(state)

    assert captured["query"] == "How do I restart the service?"
    assert captured["limit"] == settings.rag_retrieval_limit

@pytest.mark.asyncio
async def test_classify_question_returns_retrieval_true(monkeypatch):
    class FakeClassificationChain:
        async def ainvoke(self, payload):
            assert payload == {
                "question": "How do I restart the payments service?"
            }

            return RAGQuestionClassification(
                requires_retrieval=True
            )

    monkeypatch.setattr(
        "app.graphs.rag_nodes.classification_chain",
        FakeClassificationChain(),
    )

    state = {
        "question": "How do I restart the payments service?"
    }

    result = await classify_question(state)

    assert result == {
        "requires_retrieval": True
    }


@pytest.mark.asyncio
async def test_classify_question_returns_retrieval_false(monkeypatch):
    class FakeClassificationChain:
        async def ainvoke(self, payload):
            return RAGQuestionClassification(
                requires_retrieval=False
            )

    monkeypatch.setattr(
        "app.graphs.rag_nodes.classification_chain",
        FakeClassificationChain(),
    )

    state = {
        "question": "What does HTTP 500 mean?"
    }

    result = await classify_question(state)

    assert result == {
        "requires_retrieval": False
    }

@pytest.mark.asyncio
async def test_generate_answer_uses_rag_chain_when_retrieval_is_required(
    monkeypatch,
):
    class FakeRAGChain:
        async def ainvoke(self, payload):
            assert payload == {
                "question": "Who commands Snake's support team?",
                "context": "The support team is commanded by Roy Campbell.",
            }

            return "Roy Campbell commands the support team."

    monkeypatch.setattr(
        "app.graphs.rag_nodes.rag_answer_chain",
        FakeRAGChain(),
    )

    state = {
        "question": "Who commands Snake's support team?",
        "requires_retrieval": True,
        "context": "The support team is commanded by Roy Campbell.",
    }

    result = await generate_answer(state)

    assert result == {
        "answer": "Roy Campbell commands the support team."
    }


@pytest.mark.asyncio
async def test_generate_answer_uses_direct_chain_when_retrieval_is_not_required(
    monkeypatch,
):
    class FakeDirectChain:
        async def ainvoke(self, payload):
            assert payload == {
                "question": "What does HTTP 500 mean?"
            }

            return "HTTP 500 means Internal Server Error."

    monkeypatch.setattr(
        "app.graphs.rag_nodes.direct_answer_chain",
        FakeDirectChain(),
    )

    state = {
        "question": "What does HTTP 500 mean?",
        "requires_retrieval": False,
    }

    result = await generate_answer(state)

    assert result == {
        "answer": "HTTP 500 means Internal Server Error."
    }