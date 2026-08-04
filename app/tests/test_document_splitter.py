import pytest
from langchain_core.documents import Document
from types import SimpleNamespace

from app.core.exceptions import DocumentProcessingException
from app.services import document_splitter

def test_split_documents_returns_documents() -> None:
    result = document_splitter.split_documents(
        [
            "This is a document that needs to be split into chunks."
        ]
    )

    assert isinstance(result, list)
    assert isinstance(result[0], Document)

def test_split_documents_accepts_multiple_texts() -> None:
    result = document_splitter.split_documents(
        [
            "First document content",
            "Second document content",
        ]
    )

    assert len(result) > 0
    assert all(
        isinstance(document, Document)
        for document in result
    )

def test_split_documents_raises_when_texts_are_empty() -> None:
    with pytest.raises(DocumentProcessingException):
        document_splitter.split_documents([])

def test_split_documents_raises_when_text_contains_only_spaces() -> None:
    with pytest.raises(DocumentProcessingException):
        document_splitter.split_documents(
            [
                "Valid document",
                "   ",
            ]
        )

def test_split_documents_raises_document_processing_exception_when_splitter_fails(monkeypatch) -> None:
    def mock_create_documents(texts):
        raise RuntimeError("Splitter unavailable")

    monkeypatch.setattr(
        document_splitter,
        "text_splitter",
        SimpleNamespace(
            create_documents=mock_create_documents,
        ),
    )

    with pytest.raises(DocumentProcessingException):
        document_splitter.split_documents(
            [
                "Document content"
            ]
        )