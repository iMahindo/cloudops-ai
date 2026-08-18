from pathlib import Path

import pytest

from app.services import file_reader


def test_read_file_returns_content_from_str_path(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Hello CloudOps", encoding="utf-8")

    content = file_reader.read_file(str(file_path))

    assert content == "Hello CloudOps"


def test_read_file_returns_content_from_path_object(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Path object read", encoding="utf-8")

    content = file_reader.read_file(file_path)

    assert content == "Path object read"


def test_read_file_raises_when_file_not_found(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError, match="File not found"):
        file_reader.read_file(missing_file)


def test_read_file_raises_when_path_is_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Path is not a file"):
        file_reader.read_file(tmp_path)