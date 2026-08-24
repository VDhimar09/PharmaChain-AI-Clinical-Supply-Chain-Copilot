import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _redact_request_target(span, scope) -> None:
    """Prevent raw request paths and query strings from becoming span data."""

    if span and span.is_recording():
        # FastAPI's ASGI instrumentation otherwise records the full request
        # target, including query strings. Route templates remain available in
        # the span name / ``http.route`` without retaining request data.
        for attribute_name in ("http.url", "http.target", "url.full"):
            span._attributes.pop(attribute_name, None)


def configure_telemetry(app, engine) -> None:
    """Configure OpenTelemetry instrumentation for PharmaChain."""

    if getattr(app, "_pharmachain_otel_configured", False):
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "pharmachain-api")
    environment = os.getenv("OTEL_ENVIRONMENT", "development")
    service_version = os.getenv("OTEL_SERVICE_VERSION", "0.1.0")

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment.name": environment,
        }
    )

    tracer_provider = TracerProvider(resource=resource)

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if endpoint:
        exporter = OTLPSpanExporter(endpoint=endpoint)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(exporter)
        )

    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=_redact_request_target,
        http_capture_headers_server_request=[],
        http_capture_headers_server_response=[],
    )

    sqlalchemy_instrumentor = SQLAlchemyInstrumentor()
    if not sqlalchemy_instrumentor.is_instrumented_by_opentelemetry:
        sqlalchemy_instrumentor.instrument(engine=engine)

    app._pharmachain_otel_configured = True
