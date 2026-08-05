from fastapi.testclient import TestClient

from app import main

def test_lifespan_initialize_qdrant_collection(monkeypatch) -> None:
    collection_initialized = False

    def mock_create_knowledge_collection() -> None:
        nonlocal collection_initialized
        collection_initialized = True

    monkeypatch.setattr(
        main,
        "create_knowledge_collection",
        mock_create_knowledge_collection
    )

    #create and start the client
    with TestClient(main.app):
        pass

    assert collection_initialized is True