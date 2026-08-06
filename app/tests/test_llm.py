import pytest
from types import SimpleNamespace


from app.core.exceptions import LLMServiceException
from app.services import llm

#Define the tests
@pytest.mark.asyncio
async def test_generate_response_success(monkeypatch) -> None:
    async def mock_ainvoke(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            content= "LLm service has response succesfully and this is a mock message simulating a response"
        )

    monkeypatch.setattr(
        llm,
        "llm",
        SimpleNamespace(
            ainvoke = mock_ainvoke
        ),
    )

    response = await llm.generate_response("mock request")

    assert response == "LLm service has response succesfully and this is a mock message simulating a response"

@pytest.mark.asyncio
async def test_generate_response_exception(monkeypatch) -> None:
    async def mock_ainvoke(*args, **kwargs):
        raise Exception("Mock API Error")

    monkeypatch.setattr(
        llm,
        "llm",
        SimpleNamespace(
            ainvoke=mock_ainvoke,
        ),
    )

    with pytest.raises(LLMServiceException):
        await llm.generate_response("mock request")

@pytest.mark.asyncio
async def test_generate_response_raises_exception_when_content_is_none(monkeypatch) -> None:
    async def mock_ainvoke(*args, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            content = None
        )

    monkeypatch.setattr(
        llm,
        "llm",
        SimpleNamespace(
            ainvoke = mock_ainvoke
        ),
    )

    with pytest.raises(LLMServiceException):
        await llm.generate_response("mock request")