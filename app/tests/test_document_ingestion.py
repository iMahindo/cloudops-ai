import pytest
from types import SimpleNamespace

from langchain_core.documents import Document
from hashlib import sha256

from app.services import document_ingestion
from app.core.exceptions import DocumentIngestionException

def test_ingest_markdown_file_loads_splits_and_stores_documents(monkeypatch) -> None:
    stored_documents = []

    def mock_load_markdown_file(path):
        return "Markdown content"

    def mock_split_documents(texts, metadatas=None):
        return [
            Document(
                page_content="Chunk content"
            )
        ]

    mock_vector_store = SimpleNamespace(
        add_documents=lambda documents: stored_documents.extend(documents)
    )

    def mock_get_vector_store():
        return mock_vector_store

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        mock_load_markdown_file,
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        mock_get_vector_store,
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert len(stored_documents) == 1
    assert stored_documents[0].page_content == "Chunk content"

def test_ingest_markdown_file_passes_loaded_content_to_splitter(monkeypatch) -> None:
    captured_texts = []

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    def mock_split_documents(texts, metadatas=None):
        captured_texts.extend(texts)

        return [
            Document(
                page_content="Chunk"
            )
        ]

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert captured_texts == [
        "Markdown content"
    ]

def test_ingest_markdown_file_raises_document_ingestion_exception_when_storage_fails(monkeypatch) -> None:

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk"
            )
        ],
    )

    def mock_get_vector_store():
        raise RuntimeError(
            "Qdrant unavailable"
        )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        mock_get_vector_store,
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    with pytest.raises(DocumentIngestionException):
        document_ingestion.ingest_markdown_file(
            "guide.md"
        )

def test_ingest_markdown_file_passes_metadata_to_splitter(monkeypatch,tmp_path) -> None:
    file_path = tmp_path / "kubernetes.md"
    captured = {}

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Kubernetes document content",
    )

    def mock_split_documents(texts, metadatas=None):
        captured["texts"] = texts
        captured["metadatas"] = metadatas
        return [
            Document(
                page_content="Kubernetes document content",
            )
        ]

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None,
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_markdown_file(file_path)

    normalized_path = str(file_path.resolve())

    expected_document_id = sha256(
        normalized_path.encode("utf-8")
    ).hexdigest()

    assert captured["texts"] == [
        "Kubernetes document content"
    ]

    assert captured["metadatas"] == [
        {
            "document_id": expected_document_id,
            "source": normalized_path,
            "file_name": "kubernetes.md",
            "source_type": "markdown",
        }
    ]

def test_ingest_markdown_file_adds_chunk_position_metadata(monkeypatch) -> None:
    stored_documents = []

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    def mock_split_documents(texts, metadatas=None):
        return [
            Document(
                page_content="First chunk",
                metadata=metadatas[0].copy(),
            ),
            Document(
                page_content="Second chunk",
                metadata=metadatas[0].copy(),
            ),
            Document(
                page_content="Third chunk",
                metadata=metadatas[0].copy(),
            ),
        ]
    
    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: stored_documents.extend(
                documents
            ),
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert stored_documents[0].metadata["chunk_index"] == 0
    assert stored_documents[1].metadata["chunk_index"] == 1
    assert stored_documents[2].metadata["chunk_index"] == 2

    assert all(
        document.metadata["chunk_count"] == 3
        for document in stored_documents
    )

def test_ingest_markdown_files_continues_when_one_document_fails(monkeypatch) -> None:
    processed_paths = []

    def mock_ingest_markdown_file(path):
        processed_paths.append(str(path))

        if str(path) == "broken.md":
            raise DocumentIngestionException(
                "Failed to ingest document"
            )

        if str(path) == "first.md":
            return 2

        return 3

    monkeypatch.setattr(
        document_ingestion,
        "ingest_markdown_file",
        mock_ingest_markdown_file,
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    result = document_ingestion.ingest_markdown_files(
        [
            "first.md",
            "broken.md",
            "third.md",
        ]
    )

    assert processed_paths == [
        "first.md",
        "broken.md",
        "third.md",
    ]

    assert isinstance(result,document_ingestion.IngestionResult)

    assert result.documents_processed == 2
    assert result.chunks_stored == 5
    assert len(result.failed_documents) == 1

    failed_document = result.failed_documents[0]

    assert isinstance(failed_document,document_ingestion.FailedDocument)
    assert failed_document.path == "broken.md"
    assert failed_document.error == "Failed to ingest document"

def test_ingest_markdown_directory_raises_document_ingestion_exception_when_directory_does_not_exist(tmp_path, monkeypatch) -> None:
    missing_directory = tmp_path / "missing"

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    with pytest.raises(DocumentIngestionException):
        document_ingestion.ingest_markdown_directory(
            missing_directory
        )

def test_ingest_markdown_directory_raises_document_ingestion_exception_when_path_is_not_directory(tmp_path,monkeypatch) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text(
        "Markdown content",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    with pytest.raises(DocumentIngestionException):
        document_ingestion.ingest_markdown_directory(
            file_path
        )

def test_ingest_markdown_directory_finds_markdown_files_recursively(monkeypatch,tmp_path) -> None:
    knowledge_directory = tmp_path / "knowledge"
    networking_directory = knowledge_directory / "networking"

    networking_directory.mkdir(parents=True)

    root_markdown = knowledge_directory / "root.md"
    nested_markdown = networking_directory / "dns.md"
    ignored_file = knowledge_directory / "ignored.txt"

    root_markdown.write_text(
        "Root document",
        encoding="utf-8",
    )

    nested_markdown.write_text(
        "Nested document",
        encoding="utf-8",
    )

    ignored_file.write_text(
        "Ignored content",
        encoding="utf-8",
    )

    captured_paths = []

    expected_result = document_ingestion.IngestionResult(
        documents_processed=2,
        chunks_stored=4,
        failed_documents=[],
    )

    def mock_ingest_markdown_files(paths):
        captured_paths.extend(paths)
        return expected_result

    monkeypatch.setattr(
        document_ingestion,
        "ingest_markdown_files",
        mock_ingest_markdown_files,
    )

    result = document_ingestion.ingest_markdown_directory(knowledge_directory)

    assert set(captured_paths) == {
        root_markdown,
        nested_markdown,
    }

    assert result == expected_result

def test_ingest_markdown_file_deletes_existing_chunks(monkeypatch,tmp_path) -> None:
    file_path = tmp_path / "guide.md"
    captured_document_ids = []

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ],
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: captured_document_ids.append(
            document_id
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None,
        ),
    )

    document_ingestion.ingest_markdown_file(
        file_path
    )

    normalized_path = str(file_path.resolve())

    expected_document_id = sha256(
        normalized_path.encode("utf-8")
    ).hexdigest()

    assert captured_document_ids == [
        expected_document_id
    ]

def test_ingest_markdown_file_deletes_before_storing(monkeypatch) -> None:
    operations = []

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ],
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: operations.append(
            "delete"
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: operations.append(
                "store"
            ),
        ),
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert operations == [
        "delete",
        "store",
    ]

def test_ingest_markdown_files_returns_empty_result_for_empty_paths(monkeypatch) -> None:
    def mock_ingest_markdown_file(path):
        raise AssertionError(
            "ingest_markdown_file should not be called"
        )

    monkeypatch.setattr(
        document_ingestion,
        "ingest_markdown_file",
        mock_ingest_markdown_file,
    )

    result = document_ingestion.ingest_markdown_files([])

    assert isinstance(
        result,
        document_ingestion.IngestionResult,
    )

    assert result.documents_processed == 0
    assert result.chunks_stored == 0
    assert result.failed_documents == []