from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

TRACER_NAME = "async-endpoints"

_tracer: trace.Tracer | None = None


def setup_tracing() -> None:
    global _tracer
    resource = Resource.create({"service.name": TRACER_NAME})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(TRACER_NAME)


def get_tracer() -> trace.Tracer:
    if _tracer is None:
        setup_tracing()
    return _tracer  # type: ignore[return-value]


def inject_trace_context() -> dict:
    from opentelemetry.propagate import inject

    carrier: dict = {}
    inject(carrier)
    return carrier


def extract_trace_context(carrier: dict) -> object:
    from opentelemetry.propagate import extract

    return extract(carrier)
