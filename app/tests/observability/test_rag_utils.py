import pytest
from types import SimpleNamespace

from app.observability import rag_utils


@pytest.mark.asyncio
async def test_observe_rag_node_async(monkeypatch):
    calls = SimpleNamespace(duration=0)

    fake_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        rag_utils,
        "RAG_NODES_DURATION_SECONDS",
        fake_metric,
    )

    async def async_node(state):
        return {
            "answer": "ok"
        }

    wrapped_node = rag_utils.observe_rag_node(
        "generate_answer",
        async_node,
    )

    result = await wrapped_node({})

    assert result == {"answer": "ok"}
    assert calls.duration == 1


@pytest.mark.asyncio
async def test_observe_rag_node_sync(monkeypatch):
    calls = SimpleNamespace(duration=0)

    fake_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        rag_utils,
        "RAG_NODES_DURATION_SECONDS",
        fake_metric,
    )

    def sync_node(state):
        return {
            "is_valid": True
        }

    wrapped_node = rag_utils.observe_rag_node(
        "validate_answer",
        sync_node,
    )

    result = await wrapped_node({})

    assert result == {"is_valid": True}
    assert calls.duration == 1


@pytest.mark.asyncio
async def test_observe_rag_node_records_duration_when_node_fails(
    monkeypatch,
):
    calls = SimpleNamespace(duration=0)

    fake_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: setattr(
                calls,
                "duration",
                calls.duration + 1,
            )
        )
    )

    monkeypatch.setattr(
        rag_utils,
        "RAG_NODES_DURATION_SECONDS",
        fake_metric,
    )

    async def failing_node(state):
        raise RuntimeError("Node failed")

    wrapped_node = rag_utils.observe_rag_node(
        "generate_answer",
        failing_node,
    )

    with pytest.raises(RuntimeError):
        await wrapped_node({})

    assert calls.duration == 1

@pytest.mark.asyncio
async def test_observe_rag_node_creates_span_with_node_attribute(
    monkeypatch,
):
    calls = SimpleNamespace(
        span_name=None,
        attribute_name=None,
        attribute_value=None,
    )

    fake_span = SimpleNamespace(
        set_attribute=lambda name, value: (
            setattr(calls, "attribute_name", name),
            setattr(calls, "attribute_value", value),
        )
    )

    class FakeSpanContextManager:
        def __enter__(self):
            return fake_span

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    fake_tracer = SimpleNamespace(
        start_as_current_span=lambda name: (
            setattr(calls, "span_name", name)
            or FakeSpanContextManager()
        )
    )

    fake_metric = SimpleNamespace(
        labels=lambda **kwargs: SimpleNamespace(
            observe=lambda value: None
        )
    )

    monkeypatch.setattr(
        rag_utils,
        "tracer",
        fake_tracer,
    )

    monkeypatch.setattr(
        rag_utils,
        "RAG_NODES_DURATION_SECONDS",
        fake_metric,
    )

    async def node(state):
        return {"answer": "ok"}

    wrapped_node = rag_utils.observe_rag_node(
        "generate_answer",
        node,
    )

    result = await wrapped_node({})

    assert result == {"answer": "ok"}
    assert calls.span_name == "rag.generate_answer"
    assert calls.attribute_name == "rag.node"
    assert calls.attribute_value == "generate_answer"