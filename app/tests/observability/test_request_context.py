from types import SimpleNamespace

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.middleware import request_context


@pytest.mark.asyncio
async def test_request_context_success(monkeypatch):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
    }

    request = Request(scope)

    async def mock_call_next(request):
        return Response(status_code=200)

    calls = SimpleNamespace(
        total=0,
        errors=0,
        duration=0,
    )

    #fake the metrics
    fake_total_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(calls, "total", calls.total + 1)
        )
    )
    fake_error_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(calls, "errors", calls.errors + 1)
        )
    )
    fake_duration_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1
            )
        )
    )

    monkeypatch.setattr(
    request_context,
    "HTTP_REQUESTS_TOTAL",
    fake_total_metric
    )

    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_ERRORS_TOTAL",
        fake_error_metric
    )

    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_DURATION_SECONDS",
        fake_duration_metric
    )

    response = await request_context.request_context_middleware(
        request,
        mock_call_next
    )

    assert response.status_code == 200
    assert calls.total == 1
    assert calls.errors == 0
    assert calls.duration == 1

@pytest.mark.asyncio
async def test_request_context_client_error(monkeypatch):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/does-not-exist",
        "headers": [],
    }

    request = Request(scope)

    async def mock_call_next(request):
        return Response(status_code=404)

    calls = SimpleNamespace(
        total=0,
        errors=0,
        duration=0,
    )

    fake_total_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "total",
                calls.total + 1,
            )
        )
    )

    fake_error_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "errors",
                calls.errors + 1,
            )
        )
    )

    fake_duration_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        request_context,
        "HTTP_REQUESTS_TOTAL",
        fake_total_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_ERRORS_TOTAL",
        fake_error_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_DURATION_SECONDS",
        fake_duration_metric,
    )

    response = await request_context.request_context_middleware(
        request,
        mock_call_next,
    )

    assert response.status_code == 404
    assert calls.total == 1
    assert calls.errors == 1
    assert calls.duration == 1


@pytest.mark.asyncio
async def test_request_context_server_error(monkeypatch):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test-error",
        "headers": [],
    }

    request = Request(scope)

    async def mock_call_next(request):
        raise RuntimeError("Test error")

    calls = SimpleNamespace(
        total=0,
        errors=0,
        duration=0,
        status_code=None,
    )

    def total_labels(**kwargs):
        calls.status_code = kwargs["status_code"]

        return SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "total",
                calls.total + 1,
            )
        )

    fake_total_metric = SimpleNamespace(
        labels=total_labels
    )

    fake_error_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "errors",
                calls.errors + 1,
            )
        )
    )

    fake_duration_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        request_context,
        "HTTP_REQUESTS_TOTAL",
        fake_total_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_ERRORS_TOTAL",
        fake_error_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_DURATION_SECONDS",
        fake_duration_metric,
    )

    with pytest.raises(RuntimeError):
        await request_context.request_context_middleware(
            request,
            mock_call_next
        )

    assert calls.total == 1
    assert calls.errors == 1
    assert calls.duration == 1
    assert calls.status_code == "500"


@pytest.mark.asyncio
async def test_metrics_endpoint_is_excluded(monkeypatch):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/metrics",
        "headers": [],
    }

    request = Request(scope)

    async def mock_call_next(request):
        return Response(status_code=200)

    calls = SimpleNamespace(
        total=0,
        errors=0,
        duration=0,
    )

    fake_total_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "total",
                calls.total + 1,
            )
        )
    )

    fake_error_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            inc=lambda: setattr(
                calls,
                "errors",
                calls.errors + 1,
            )
        )
    )

    fake_duration_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        request_context,
        "HTTP_REQUESTS_TOTAL",
        fake_total_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_ERRORS_TOTAL",
        fake_error_metric,
    )
    monkeypatch.setattr(
        request_context,
        "HTTP_REQUEST_DURATION_SECONDS",
        fake_duration_metric,
    )

    response = await request_context.request_context_middleware(
        request,
        mock_call_next,
    )

    assert response.status_code == 200
    assert calls.total == 0
    assert calls.errors == 0
    assert calls.duration == 0


@pytest.mark.asyncio
async def test_request_id_is_added_to_response_header():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
    }

    request = Request(scope)

    async def mock_call_next(request):
        return Response(status_code=200)

    response = await request_context.request_context_middleware(
        request,
        mock_call_next
    )

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]