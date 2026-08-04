import pytest
from pathlib import Path

from app.services import document_loader


def test_read_file_returns_content_from_str_path(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Hello CloudOps", encoding="utf-8")

    content = document_loader.read_file(str(file_path))

    assert content == "Hello CloudOps"


def test_read_file_returns_content_from_path_object(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Path object read", encoding="utf-8")

    content = document_loader.read_file(file_path)

    assert content == "Path object read"


def test_read_file_raises_when_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError, match="File not found"):
        document_loader.read_file(missing_file)


def test_read_file_raises_when_path_is_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Path is not a file"):
        document_loader.read_file(tmp_path)


def test_load_markdown_file_returns_content(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.md"
    file_path.write_text("# CloudOps Guide", encoding="utf-8")

    content = document_loader.load_markdown_file(file_path)

    assert content == "# CloudOps Guide"


def test_load_markdown_file_accepts_uppercase_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.MD"
    file_path.write_text("Markdown content", encoding="utf-8")

    content = document_loader.load_markdown_file(file_path)

    assert content == "Markdown content"


def test_load_markdown_file_raises_when_not_markdown(tmp_path: Path) -> None:
    file_path = tmp_path / "guide.txt"
    file_path.write_text("Plain text", encoding="utf-8")

    with pytest.raises(ValueError, match="File is not a Markdown file"):
        document_loader.load_markdown_file(file_path)


def test_load_markdown_file_raises_when_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError, match="File not found"):
        document_loader.load_markdown_file(missing_file)

def test_load_markdown_file_raises_when_path_is_directory(tmp_path: Path) -> None:
    directory_path = tmp_path / "docs.md"
    directory_path.mkdir()

    with pytest.raises(ValueError, match="Path is not a file"):
        document_loader.load_markdown_file(directory_path)