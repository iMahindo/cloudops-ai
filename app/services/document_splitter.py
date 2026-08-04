from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import DocumentProcessingException


logger = get_logger(__name__)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
)

def split_documents(texts: list[str]) -> list[Document]:
    try:
        logger.info("Splitting %s documents into chunks",len(texts))

        if not texts:
            raise ValueError("Texts cannot be empty")

        if any(not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty values")
        
        return text_splitter.create_documents(texts)
    except Exception as exc:
        logger.exception("Failed to split documents")
        raise DocumentProcessingException("Failed to split documents") from exc


    