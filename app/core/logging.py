import logging
import sys

from app.core.config import settings

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT, stream=sys.stdout)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
