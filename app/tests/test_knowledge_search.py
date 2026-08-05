import pytest
from types import SimpleNamespace

from langchain_core.documents import Document

from app.services import knowledge_search
from app.core.exceptions import KnowledgeSearchException


def test_search_knowledge_rejects_empty_query() -> None:
    with pytest.raises(KnowledgeSearchException, match="Search query cannot be empty"):
        knowledge_search.search_knowledge("   ", limit=5)


def test_search_knowledge_rejects_limit_less_than_one() -> None:
    with pytest.raises(KnowledgeSearchException, match="Search limit must be greater than zero"):
        knowledge_search.search_knowledge("cloud networking", limit=0)


def test_search_knowledge_returns_results(monkeypatch) -> None:
    captured_arguments = {}

    mock_documents = [
        Document(
            page_content="How to configure VPC peering",
            metadata={"document_id": "doc-1", "source": "networking.md"},
        ),
        Document(
            page_content="Kubernetes ingress troubleshooting",
            metadata={"document_id": "doc-2", "source": "k8s.md"},
        ),
    ]

    def mock_similarity_search(query, k):
        captured_arguments["query"] = query
        captured_arguments["k"] = k
        return mock_documents

    mock_vector_store = SimpleNamespace(
        similarity_search=mock_similarity_search,
    )

    monkeypatch.setattr(
        knowledge_search,
        "get_vector_store",
        lambda: mock_vector_store,
    )

    response = knowledge_search.search_knowledge("VPC peering", limit=2)

    assert captured_arguments == {"query": "VPC peering", "k": 2}
    assert len(response.results) == 2
    assert response.results[0].content == "How to configure VPC peering"
    assert response.results[0].metadata == {
        "document_id": "doc-1",
        "source": "networking.md",
    }
    assert response.results[1].content == "Kubernetes ingress troubleshooting"
    assert response.results[1].metadata == {
        "document_id": "doc-2",
        "source": "k8s.md",
    }


def test_search_knowledge_returns_empty_results_when_no_documents_found(monkeypatch) -> None:
    mock_vector_store = SimpleNamespace(
        similarity_search=lambda query, k: [],
    )

    monkeypatch.setattr(
        knowledge_search,
        "get_vector_store",
        lambda: mock_vector_store,
    )

    response = knowledge_search.search_knowledge("unknown topic", limit=5)

    assert response.results == []


def test_search_knowledge_raises_knowledge_search_exception_when_vector_store_fails(monkeypatch) -> None:
    def mock_get_vector_store():
        raise RuntimeError("Qdrant is not available")

    monkeypatch.setattr(
        knowledge_search,
        "get_vector_store",
        mock_get_vector_store,
    )

    with pytest.raises(KnowledgeSearchException, match="Failed to search knowledge base"):
        knowledge_search.search_knowledge("cloud networking", limit=5)


def test_search_knowledge_raises_knowledge_search_exception_when_similarity_search_fails(monkeypatch) -> None:
    def mock_similarity_search(query, k):
        raise RuntimeError("Similarity search failed")

    mock_vector_store = SimpleNamespace(
        similarity_search=mock_similarity_search,
    )

    monkeypatch.setattr(
        knowledge_search,
        "get_vector_store",
        lambda: mock_vector_store,
    )

    with pytest.raises(KnowledgeSearchException, match="Failed to search knowledge base"):
        knowledge_search.search_knowledge("cloud networking", limit=5)
