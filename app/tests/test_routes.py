from fastapi.testclient import TestClient

from app.core.exceptions import KnowledgeSearchException, LLMServiceException, RAGServiceException
from app.main import app
from app.api import routes
from app.schemas.knowledge_search import KnowledgeSearchResponse, KnowledgeSearchResult
from app.schemas.rag import RAGResponse, RAGSource

#create the client
client = TestClient(app)

#Define the tests
def test_empty_prompt_returns_validation_error()-> None:
    response = client.post(
        "/chat",
        json={
            "prompt": ""
        }
    )

    assert response.status_code == 422

def test_chat_returns_generated_response(monkeypatch) -> None:
    async def mock_generate_response(prompt : str) -> str:
        return "mock response generated"
    
    monkeypatch.setattr(
        routes,
        "generate_response",
        mock_generate_response,
    )

    response = client.post(
        "/chat",
        json={
            "prompt": "Mock request for generated response"
        }
    )

    assert response.status_code == 200
    assert response.json()=={
        "response" : "mock response generated"
    }

def test_chat_returns_exception(monkeypatch) -> None:
    async def mock_generate_response(prompt: str) -> str:
        raise LLMServiceException(
            "The LLM provider failed to generate a response"
        )
    
    monkeypatch.setattr(
        routes,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/chat",
        json={
            "prompt": "Mock request for generated response"
        }
    )

    assert response.status_code == 503
    assert response.json()=={
        "detail": "The model service is temporarily unavailable"
    }

def test_empty_query_returns_validation_error() -> None:
    response = client.post(
        "/knowledge/search",
        json={
            "query": "",
        },
    )

    assert response.status_code == 422

def test_search_knowledge_returns_results(monkeypatch) -> None:
    captured_arguments = {}

    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        captured_arguments["query"] = query
        captured_arguments["limit"] = limit
        return KnowledgeSearchResponse(
            results=[
                KnowledgeSearchResult(
                    content="How to configure VPC peering",
                    metadata={"document_id": "doc-1", "source": "networking.md"},
                )
            ]
        )

    monkeypatch.setattr(
        routes,
        "search_knowledge",
        mock_search_knowledge,
    )

    response = client.post(
        "/knowledge/search",
        json={
            "query": "VPC peering",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "content": "How to configure VPC peering",
                "metadata": {
                    "document_id": "doc-1",
                    "source": "networking.md",
                },
            }
        ]
    }
    assert captured_arguments == {
        "query": "VPC peering",
        "limit": 5,
    }

def test_search_knowledge_returns_exception(monkeypatch) -> None:
    async def mock_search_knowledge(query: str, limit: int) -> KnowledgeSearchResponse:
        raise KnowledgeSearchException(
            "Failed to search knowledge base"
        )

    monkeypatch.setattr(
        routes,
        "search_knowledge",
        mock_search_knowledge,
    )

    response = client.post(
        "/knowledge/search",
        json={
            "query": "VPC peering",
            "limit": 5,
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The knowledge service is temporarily unavailable",
    }

def test_rag_ask_returns_results(monkeypatch) -> None:
    captured_arguments = {}
    async def mock_generate_rag_response(question: str) -> RAGResponse:
        captured_arguments["question"] = question
        return RAGResponse(
            answer = "RAG answer example",
            sources=[
                RAGSource(name = "test.md", chunk_index = 1),
                RAGSource(name = "test2.md", chunk_index = 4)
            ]
        )
    
    monkeypatch.setattr(
        routes,
        "generate_rag_response",
        mock_generate_rag_response
    )

    response = client.post(
        "/rag/ask",
        json={
            "question": "User question test",
        }
    )

    assert captured_arguments == {
        "question":  "User question test"
    }
    assert response.status_code == 200
    assert response.json() == {
        "answer": "RAG answer example",
        "sources": [
            {
                "name": "test.md",
                "chunk_index": 1
            },
            {
                "name": "test2.md",
                "chunk_index": 4
            }
        ]
    }

def test_rag_ask_rejects_empty_question() -> None:
    response = client.post(
        "/rag/ask",
        json={
            "question": "",
        },
    )

    assert response.status_code == 422

def test_rag_ask_returns_rag_service_exception(monkeypatch) -> None:
    async def mock_generate_rag_response(question: str) -> RAGResponse:
        raise RAGServiceException(
            "Failed to asking the question to rag"
        )
    
    monkeypatch.setattr(
        routes,
        "generate_rag_response",
        mock_generate_rag_response
    )
    
    response = client.post(
        "/rag/ask",
        json={
            "question": "User question test",
        }
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The RAG service is temporarily unavailable",
    }

def test_upload_knowledge_document_returns_result(monkeypatch) -> None:
    captured_arguments = {}

    def mock_ingest_uploaded_markdown(file_name: str,content: bytes) -> int:
        captured_arguments["file_name"] = file_name
        captured_arguments["content"] = content
        return 3

    monkeypatch.setattr(
        routes,
        "ingest_uploaded_markdown",
        mock_ingest_uploaded_markdown,
    )

    response = client.post(
        "/knowledge/upload",
        files={
            "file": (
                "guide.md",
                b"# CloudOps Guide",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "file_name": "guide.md",
        "chunks_stored": 3,
    }

    assert captured_arguments == {
        "file_name": "guide.md",
        "content": b"# CloudOps Guide",
    }

def test_upload_knowledge_document_returns_validation_error_when_file_is_missing() -> None:
    response = client.post(
        "/knowledge/upload"
    )

    assert response.status_code == 422

def test_upload_knowledge_document_returns_service_exception(monkeypatch) -> None:
    def mock_ingest_uploaded_markdown(file_name: str, content: bytes) -> int:
        raise RuntimeError(
            "Qdrant unavailable"
        )

    monkeypatch.setattr(
        routes,
        "ingest_uploaded_markdown",
        mock_ingest_uploaded_markdown,
    )

    response = client.post(
        "/knowledge/upload",
        files={
            "file": (
                "guide.md",
                b"# CloudOps Guide",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The upload service is temporarily unavailable",
    }

def test_upload_knowledge_document_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/knowledge/upload",
        files={
            "file": (
                "guide.txt",
                b"Plain text content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "File is not a Markdown file: guide.txt"
    }

def test_read_root_returns_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CloudOps AI" in response.text

def test_notion_ingestion_returns_result(monkeypatch) -> None:
    captured_arguments = {}

    def fake_ingest_notion_page(page_id: str) -> int:
        captured_arguments["page_id"] = page_id
        return 3

    monkeypatch.setattr(
        routes,
        "ingest_notion_page",
        fake_ingest_notion_page,
    )

    response = client.post(
        "/knowledge/notion",
        json={
            "page_id": "page-123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "page_id": "page-123",
        "chunks_stored": 3,
    }
    assert captured_arguments["page_id"] == "page-123"

def test_notion_ingestion_rejects_empty_page_id() -> None:
    response = client.post(
        "/knowledge/notion",
        json={
            "page_id": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Notion page ID must not be empty"
    }

def test_notion_ingestion_returns_503_on_service_error(monkeypatch) -> None:
    def fake_ingest_notion_page(page_id: str) -> int:
        raise RuntimeError("Notion unavailable")

    monkeypatch.setattr(
        routes,
        "ingest_notion_page",
        fake_ingest_notion_page,
    )

    response = client.post(
        "/knowledge/notion",
        json={
            "page_id": "page-123",
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The notion ingestion service is temporarily unavailable"
    }