from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


def read_file(path: str | Path) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    logger.info("Reading file from %s", file_path)

    return file_path.read_text(encoding="utf-8")