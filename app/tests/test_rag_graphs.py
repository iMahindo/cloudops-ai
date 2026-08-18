import pytest

from app.graphs import rag_nodes
from app.graphs.rag_graphs import build_rag_graph
from app.schemas.rag import RAGQuestionClassification


@pytest.mark.asyncio
async def test_rag_graphs_follows_direct_route(monkeypatch):
    class FakeClassificationChain:
        async def ainvoke(self, payload):
            return RAGQuestionClassification(
                requires_retrieval=False
            )

    class FakeDirectAnswerChain:
        async def ainvoke(self, payload):
            return "HTTP 500 means Internal Server Error."

    monkeypatch.setattr(
        rag_nodes,
        "classification_chain",
        FakeClassificationChain(),
    )
    monkeypatch.setattr(
        rag_nodes,
        "direct_answer_chain",
        FakeDirectAnswerChain(),
    )

    graph = build_rag_graph()

    result = await graph.ainvoke(
        {
            "question": "What does HTTP 500 mean?"
        }
    )

    assert result["requires_retrieval"] is False
    assert result["answer"] == "HTTP 500 means Internal Server Error."
    assert result["is_valid"] is True
    assert "context" not in result
    assert "sources" not in result


@pytest.mark.asyncio
async def test_rag_graphs_follows_retrieval_route(monkeypatch):
    class FakeClassificationChain:
        async def ainvoke(self, payload):
            return RAGQuestionClassification(
                requires_retrieval=True
            )

    class FakeRAGAnswerChain:
        async def ainvoke(self, payload):
            return "Roy Campbell commands Snake's support team."

    async def fake_search_knowledge(query: str, limit: int):
        class Result:
            def __init__(self):
                self.content = "The support team is commanded by Roy Campbell."
                self.metadata = {
                    "file_name": "mgs_knowledge.md",
                    "chunk_index": 0,
                }

        class SearchResponse:
            def __init__(self):
                self.results = [Result()]

        return SearchResponse()

    monkeypatch.setattr(
        rag_nodes,
        "classification_chain",
        FakeClassificationChain(),
    )
    monkeypatch.setattr(
        rag_nodes,
        "rag_answer_chain",
        FakeRAGAnswerChain(),
    )
    monkeypatch.setattr(
        rag_nodes,
        "search_knowledge",
        fake_search_knowledge,
    )

    graph = build_rag_graph()

    result = await graph.ainvoke(
        {
            "question": "Who commands Snake's support team?"
        }
    )

    assert result["requires_retrieval"] is True
    assert (
        result["context"]
        == "The support team is commanded by Roy Campbell."
    )
    assert result["answer"] == (
        "Roy Campbell commands Snake's support team."
    )
    assert result["is_valid"] is True
    assert len(result["sources"]) == 1
    assert result["sources"][0].name == "mgs_knowledge.md"
    assert result["sources"][0].chunk_index == 0