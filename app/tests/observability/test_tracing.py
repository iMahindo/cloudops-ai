from app.observability import tracing


def test_setup_tracing_does_not_create_exporter_without_endpoint(monkeypatch) -> None:
    exporter_created = False

    def fake_exporter(*args, **kwargs):
        nonlocal exporter_created
        exporter_created = True
        raise AssertionError("OTLP exporter must not be created")

    monkeypatch.setattr(
        tracing.settings,
        "otlp_traces_endpoint",
        None,
    )
    monkeypatch.setattr(
        tracing,
        "OTLPSpanExporter",
        fake_exporter,
    )

    tracing.setup_tracing()

    assert exporter_created is False