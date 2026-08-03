import pytest
from types import SimpleNamespace


from app.core.exceptions import LLMServiceException
from app.services import llm
from app.services.llm import generate_response

#Define the tests
@pytest.mark.asyncio
async def test_generate_response_success(monkeypatch) -> None:
    async def mock_create(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message = SimpleNamespace(
                        content= "LLm service has response succesfully and this is a mock message simulating a response"
                    )
                )
            ]
        )

    monkeypatch.setattr(
        llm.client.chat.completions,
        "create",
        mock_create,
    )

    response = await generate_response("mock request")

    assert response == "LLm service has response succesfully and this is a mock message simulating a response"

@pytest.mark.asyncio
async def test_generate_response_exception(monkeypatch) -> None:
    async def mock_create(*args, **kwargs):
        raise Exception("Mock API Error")

    monkeypatch.setattr(
        llm.client.chat.completions,
        "create",
        mock_create,
    )

    with pytest.raises(LLMServiceException):
        await generate_response("mock request")

@pytest.mark.asyncio
async def test_generate_response_raises_exception_when_content_is_none(monkeypatch) -> None:
    async def mock_create(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message = SimpleNamespace(
                        content= None
                    )
                )
            ]
        )

    monkeypatch.setattr(
        llm.client.chat.completions,
        "create",
        mock_create,
    )

    with pytest.raises(LLMServiceException):
        await generate_response("mock request")