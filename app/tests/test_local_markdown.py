from hashlib import sha256
from pathlib import Path

import pytest

from app.schemas.knowledge import KnowledgeDocument
from app.sources import local_markdown


def test_load_markdown_document_returns_knowledge_document(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text(
        "# CloudOps Guide",
        encoding="utf-8",
    )

    document = local_markdown.load_markdown_document(file_path)

    normalized_path = str(file_path.resolve())

    expected_document_id = sha256(
        normalized_path.encode("utf-8")
    ).hexdigest()

    assert isinstance(
        document,
        KnowledgeDocument,
    )

    assert document.document_id == expected_document_id
    assert document.content == "# CloudOps Guide"

    assert document.metadata == {
        "document_id": expected_document_id,
        "source": normalized_path,
        "file_name": "guide.md",
        "source_type": "markdown",
    }


def test_load_markdown_document_accepts_str_path(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text(
        "Markdown content",
        encoding="utf-8",
    )

    document = local_markdown.load_markdown_document(
        str(file_path)
    )

    assert document.content == "Markdown content"


def test_load_markdown_document_raises_when_file_does_not_exist(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
        local_markdown.load_markdown_document(
            missing_file
        )


def test_load_markdown_document_raises_when_file_is_not_markdown(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.txt"
    file_path.write_text(
        "Plain text",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        local_markdown.load_markdown_document(
            file_path
        )


def test_load_markdown_documents_returns_all_documents(tmp_path: Path) -> None:
    first_file = tmp_path / "first.md"
    second_file = tmp_path / "second.md"

    first_file.write_text(
        "First document",
        encoding="utf-8",
    )

    second_file.write_text(
        "Second document",
        encoding="utf-8",
    )

    documents = local_markdown.load_markdown_documents(
        [
            first_file,
            second_file,
        ]
    )

    assert len(documents) == 2

    assert documents[0].content == "First document"
    assert documents[1].content == "Second document"


def test_load_markdown_documents_returns_empty_list_for_empty_paths() -> None:
    documents = local_markdown.load_markdown_documents(
        []
    )

    assert documents == []


def test_load_markdown_directory_finds_markdown_files_recursively(tmp_path: Path) -> None:
    knowledge_directory = tmp_path / "knowledge"
    nested_directory = knowledge_directory / "networking"

    nested_directory.mkdir(parents=True)

    root_markdown = knowledge_directory / "root.md"
    nested_markdown = nested_directory / "dns.md"
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

    documents = local_markdown.load_markdown_directory(
        knowledge_directory
    )

    loaded_file_names = {
        document.metadata["file_name"]
        for document in documents
    }

    assert loaded_file_names == {
        "root.md",
        "dns.md",
    }


def test_load_markdown_directory_raises_when_directory_does_not_exist(tmp_path: Path) -> None:
    missing_directory = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        local_markdown.load_markdown_directory(
            missing_directory
        )


def test_load_markdown_directory_raises_when_path_is_not_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text(
        "Markdown content",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        local_markdown.load_markdown_directory(
            file_path
        )


def test_load_markdown_directory_returns_empty_list_when_no_markdown_files_exist(tmp_path: Path) -> None:
    directory = tmp_path / "knowledge"
    directory.mkdir()

    text_file = directory / "notes.txt"
    text_file.write_text(
        "Not Markdown",
        encoding="utf-8",
    )

    documents = local_markdown.load_markdown_directory(
        directory
    )

    assert documents == []

def test_load_markdown_file_returns_content(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text("# CloudOps Guide", encoding="utf-8")

    content = local_markdown.load_markdown_file(file_path)

    assert content == "# CloudOps Guide"


def test_load_markdown_file_accepts_uppercase_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.MD"
    file_path.write_text("Markdown content", encoding="utf-8")

    content = local_markdown.load_markdown_file(file_path)

    assert content == "Markdown content"


def test_load_markdown_file_raises_when_not_markdown(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.txt"
    file_path.write_text("Plain text", encoding="utf-8")

    with pytest.raises(ValueError, match="File is not a Markdown file"):
        local_markdown.load_markdown_file(file_path)


def test_load_markdown_file_raises_when_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError, match="File not found"):
        local_markdown.load_markdown_file(missing_file)

def test_load_markdown_file_raises_when_path_is_directory(tmp_path: Path) -> None:
    directory_path = tmp_path / "docs.md"
    directory_path.mkdir()

    with pytest.raises(ValueError, match="Path is not a file"):
        local_markdown.load_markdown_file(directory_path)