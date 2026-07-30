from fastapi.testclient import TestClient

from app.core.exceptions import LLMServiceException
from app.main import app
from app.api import routes

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