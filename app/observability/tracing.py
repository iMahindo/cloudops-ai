from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings


def setup_tracing() -> None:
    #create the resource
    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "deployment.environment.name": settings.environment
        }
    )

    #create and set the provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    #create the exporter
    exporter = OTLPSpanExporter(
        endpoint=settings.otlp_traces_endpoint
    )
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

