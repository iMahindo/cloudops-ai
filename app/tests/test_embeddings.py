import pytest
from types import SimpleNamespace

from app.core.exceptions import EmbeddingServiceException
from app.services import embeddings


def test_generate_document_embeddings_returns_vectors(monkeypatch) -> None:
    expected_vectors = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    def mock_embed_documents(texts):
        return expected_vectors

    mock_embedding_model = SimpleNamespace(
        embed_documents=mock_embed_documents,
    )

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        mock_embedding_model,
    )

    result = embeddings.generate_document_embeddings(
        [
            "First chunk",
            "Second chunk",
        ]
    )

    assert result == expected_vectors


def test_generate_document_embeddings_rejects_empty_list() -> None:
    with pytest.raises(EmbeddingServiceException):
        embeddings.generate_document_embeddings([])


def test_generate_document_embeddings_rejects_empty_text() -> None:
    with pytest.raises(EmbeddingServiceException):
        embeddings.generate_document_embeddings(
            [
                "Valid chunk",
                "   ",
            ]
        )


def test_generate_document_embeddings_uses_expected_texts(monkeypatch) -> None:
    captured_texts = []

    def mock_embed_documents(texts):
        captured_texts.extend(texts)
        return [[0.1], [0.2]]

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        SimpleNamespace(
            embed_documents=mock_embed_documents,
        ),
    )

    embeddings.generate_document_embeddings(
        [
            "First chunk",
            "Second chunk",
        ]
    )

    assert captured_texts == [
        "First chunk",
        "Second chunk",
    ]


def test_generate_document_embeddings_raises_embedding_service_exception(monkeypatch) -> None:
    def mock_embed_documents(texts):
        raise RuntimeError("Google service unavailable")

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        SimpleNamespace(
            embed_documents=mock_embed_documents,
        ),
    )

    with pytest.raises(EmbeddingServiceException):
        embeddings.generate_document_embeddings(
            ["Example chunk"]
        )


def test_generate_query_embedding_returns_vector(monkeypatch) -> None:
    def mock_embed_query(text):
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        SimpleNamespace(
            embed_query=mock_embed_query,
        ),
    )

    result = embeddings.generate_query_embedding(
        "How do I restart the API?"
    )

    assert result == [0.1, 0.2, 0.3]


def test_generate_query_embedding_uses_expected_text(monkeypatch) -> None:
    captured_text = {}

    def mock_embed_query(text):
        captured_text["value"] = text
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        SimpleNamespace(
            embed_query=mock_embed_query,
        ),
    )

    embeddings.generate_query_embedding(
        "How do I restart the API?"
    )

    assert captured_text["value"] == "How do I restart the API?"


def test_generate_query_embedding_rejects_empty_text() -> None:
    with pytest.raises(EmbeddingServiceException):
        embeddings.generate_query_embedding("   ")


def test_generate_query_embedding_raises_embedding_service_exception(monkeypatch) -> None:
    def mock_embed_query(text):
        raise RuntimeError("Google service unavailable")

    monkeypatch.setattr(
        embeddings,
        "embedding_model",
        SimpleNamespace(
            embed_query=mock_embed_query,
        ),
    )

    with pytest.raises(EmbeddingServiceException):
        embeddings.generate_query_embedding(
            "How do I restart the API?"
        )