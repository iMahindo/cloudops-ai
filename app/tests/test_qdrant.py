from types import SimpleNamespace
import pytest


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

def test_get_collections_raises_exception_when_connection_fails(monkeypatch) -> None:
    def mock_get_collections(*args, **kwargs) -> SimpleNamespace:
        raise ConnectionError("Qdrant is not available")
    
    monkeypatch.setattr(
        qdrant.client,
        "get_collections",
        mock_get_collections
    )
    
    with pytest.raises(ConnectionError):
        qdrant.get_collections()