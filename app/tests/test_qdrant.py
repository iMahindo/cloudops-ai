from types import SimpleNamespace

import pytest
from qdrant_client.models import Distance

from app.core.config import settings
from app.core.exceptions import VectorDatabaseException
from app.services import qdrant


#Define the tests
def test_get_collections_returns_collections_names(monkeypatch) -> None:
    def mock_get_collections(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            collections=[
                SimpleNamespace(name="documents"),
                SimpleNamespace(name="runbooks")
                ]
        )
    monkeypatch.setattr(
        qdrant.client,
        "get_collections",
        mock_get_collections
    )
    collections_names = qdrant.get_collections()
    assert collections_names == [
        "documents",
        "runbooks",
    ]

def test_get_collections_returns_empty_list_when_no_collections_are_found(monkeypatch) -> None:
    def mock_get_collections(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            collections=[]
        )
    monkeypatch.setattr(
        qdrant.client,
        "get_collections",
        mock_get_collections
    )
    collections_names = qdrant.get_collections()
    
    assert collections_names == []

def test_get_collections_raises_vector_database_exception_when_connection_fails(monkeypatch) -> None:
    def mock_get_collections(*args, **kwargs) -> SimpleNamespace:
        raise ConnectionError("Qdrant is not available")
    
    monkeypatch.setattr(
        qdrant.client,
        "get_collections",
        mock_get_collections
    )
    
    with pytest.raises(VectorDatabaseException):
        qdrant.get_collections()

def test_create_knowledge_collection_does_not_create_if_exists(monkeypatch) -> None:
    create_called = False
    
    def mock_collection_exists (*args, **kwargs) -> bool:
        return True

    def mock_create_collection(*args, **kwargs) -> None:
        nonlocal create_called
        create_called = True

    monkeypatch.setattr(
        qdrant.client,
        "collection_exists",
        mock_collection_exists
    )

    monkeypatch.setattr(
        qdrant.client,
        "create_collection",
        mock_create_collection
    )

    qdrant.create_knowledge_collection()

    assert create_called is False

def test_create_knowledge_collection_creates_if_missing(monkeypatch) -> None:
    captured_arguments = {}

    def mock_collection_exists(*args, **kwargs):
        return False

    def mock_create_collection(*args, **kwargs):
        captured_arguments.update(kwargs)

    monkeypatch.setattr(
        qdrant.client,
        "collection_exists",
        mock_collection_exists,
    )

    monkeypatch.setattr(
        qdrant.client,
        "create_collection",
        mock_create_collection,
    )

    qdrant.create_knowledge_collection()

    assert captured_arguments["collection_name"] == settings.qdrant_collection
    assert captured_arguments["vectors_config"].size == settings.gemini_embedding_dimension
    assert captured_arguments["vectors_config"].distance == Distance.COSINE

def test_create_knowledge_collection_raises_vector_database_exception_when_collection_exists_fails(monkeypatch) -> None:
    def mock_collection_exists(*args, **kwargs):
        raise RuntimeError("Qdrant unavailable")

    monkeypatch.setattr(
        qdrant.client,
        "collection_exists",
        mock_collection_exists,
    )

    with pytest.raises(VectorDatabaseException):
        qdrant.create_knowledge_collection()

def test_create_knowledge_collection_raises_vector_database_exception_when_create_fails(monkeypatch) -> None:
    def mock_collection_exists(*args, **kwargs):
        return False

    def mock_create_collection(*args, **kwargs):
        raise RuntimeError("Qdrant unavailable")

    monkeypatch.setattr(
        qdrant.client,
        "collection_exists",
        mock_collection_exists,
    )

    monkeypatch.setattr(
        qdrant.client,
        "create_collection",
        mock_create_collection,
    )

    with pytest.raises(VectorDatabaseException):
        qdrant.create_knowledge_collection()

def test_get_vector_store_returns_vector_store(monkeypatch) -> None:
    captured_arguments = {}

    def mock_qdrant_vector_store(*args, **kwargs):
        captured_arguments.update(kwargs)
        return "mock_vector_store"

    monkeypatch.setattr(
        qdrant,
        "QdrantVectorStore",
        mock_qdrant_vector_store,
    )

    result = qdrant.get_vector_store()

    assert result == "mock_vector_store"
    assert captured_arguments["client"] == qdrant.client
    assert captured_arguments["collection_name"] == settings.qdrant_collection
    assert captured_arguments["embedding"] == qdrant.embedding_model

def test_get_vector_store_raises_vector_database_exception_when_creation_fails(monkeypatch) -> None:
    def mock_qdrant_vector_store(*args, **kwargs):
        raise RuntimeError("Failed creating vector store")

    monkeypatch.setattr(
        qdrant,
        "QdrantVectorStore",
        mock_qdrant_vector_store,
    )

    with pytest.raises(VectorDatabaseException):
        qdrant.get_vector_store()

def test_delete_document_chunks_uses_document_id_filter(monkeypatch) -> None:
    captured = {}

    def mock_delete(collection_name,points_selector,wait):
        captured["collection_name"] = collection_name
        captured["points_selector"] = points_selector
        captured["wait"] = wait

    monkeypatch.setattr(
        qdrant,
        "client",
        SimpleNamespace(
            delete=mock_delete,
        )
    )

    qdrant.delete_document_chunks(
        "document-123"
    )

    assert captured["collection_name"] == settings.qdrant_collection
    assert captured["wait"] is True

    selector = captured["points_selector"]
    condition = selector.filter.must[0]

    assert condition.key == "metadata.document_id"
    assert condition.match.value == "document-123"

def test_delete_document_chunks_raises_vector_database_exception_when_delete_fails(monkeypatch) -> None:
    def mock_delete(*args, **kwargs):
        raise RuntimeError(
            "Qdrant delete failed"
        )

    monkeypatch.setattr(
        qdrant,
        "client",
        SimpleNamespace(
            delete=mock_delete,
        )
    )

    with pytest.raises(VectorDatabaseException):
        qdrant.delete_document_chunks(
            "document-123"
        )