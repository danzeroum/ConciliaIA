#!/usr/bin/env python3
"""BuildToValue v7.4-Platinum - OpenTelemetry Tracer utilities."""
from __future__ import annotations

import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

OTEL_AVAILABLE = True
try:  # pragma: no cover - import guard
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
except ImportError:  # pragma: no cover - executed when dependency missing
    OTEL_AVAILABLE = False
    print(
        "⚠️ OpenTelemetry não instalado. Execute: pip install "
        "opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger",
        file=sys.stderr,
    )

try:  # pragma: no cover - optional dependency
    import yaml
except ImportError:  # pragma: no cover - gracefully degrade
    yaml = None


class BuildToValueTracer:
    """Tracer configurado para BuildToValue."""

    def __init__(self, config_file: str = "scripts/observability/telemetry-config.yaml") -> None:
        self.config_file = Path(config_file)
        self.enabled = os.getenv("BTV_TELEMETRY_ENABLED", "true").lower() == "true"
        self.config: Dict[str, Any] = self._load_config()
        self.tracer: Optional[trace.Tracer] = None

        if not OTEL_AVAILABLE:
            self.enabled = False
            return

        if self.enabled:
            self._setup_tracer()

    # ---------------------------------------------------------------------
    def _load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {}

        if yaml is None:
            print("⚠️ Dependência 'pyyaml' não instalada. Usando configuração padrão.", file=sys.stderr)
            return {}

        try:
            with self.config_file.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}
        except Exception as exc:  # pragma: no cover - config error path
            print(f"⚠️ Erro ao carregar config: {exc}", file=sys.stderr)
            return {}

    # ---------------------------------------------------------------------
    def _setup_tracer(self) -> None:
        resource_attributes = {
            "service.name": "buildtovalue",
            "service.version": "v7.4-platinum-phase2",
            "deployment.environment": os.getenv("BTV_ENVIRONMENT", "production"),
            "host.name": os.getenv("HOSTNAME", "unknown"),
        }
        resource_attributes.update(self.config.get("resource_attributes", {}))

        provider = TracerProvider(resource=Resource.create(resource_attributes))
        self._configure_exporters(provider)

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

    # ------------------------------------------------------------------
    def _configure_exporters(self, provider: TracerProvider) -> None:
        exporters_cfg = self.config.get("exporters", {})

        if exporters_cfg.get("jaeger", {}).get("enabled", True):
            agent_host = os.getenv("BTV_JAEGER_HOST", "localhost")
            agent_port = int(os.getenv("BTV_JAEGER_PORT", "6831"))
            exporter = JaegerExporter(agent_host_name=agent_host, agent_port=agent_port)
            provider.add_span_processor(BatchSpanProcessor(exporter))

        if exporters_cfg.get("otlp", {}).get("enabled", False):
            endpoint = os.getenv(
                "BTV_OTLP_ENDPOINT",
                exporters_cfg.get("otlp", {}).get("endpoint", "localhost:4317"),
            )
            protocol = exporters_cfg.get("otlp", {}).get("protocol", "grpc").lower()
            exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True if protocol == "grpc" else False)
            provider.add_span_processor(BatchSpanProcessor(exporter))

        if exporters_cfg.get("console", {}).get("enabled", False):
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # ------------------------------------------------------------------
    @contextmanager
    def start_span(
        self, name: str, attributes: Optional[Dict[str, Any]] = None
    ) -> Generator[Optional[Any], None, None]:
        if not self.enabled or not OTEL_AVAILABLE or self.tracer is None:
            yield None
            return

        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)

            try:
                yield span
            except Exception as exc:  # pragma: no cover - error path
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(exc))
                span.set_attribute("error.type", exc.__class__.__name__)
                span.record_exception(exc)
                raise

    # ------------------------------------------------------------------
    def add_event(self, span: Optional[Any], name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        if span is not None and self.enabled and OTEL_AVAILABLE:
            span.add_event(name, attributes or {})

    # ------------------------------------------------------------------
    def record_exception(self, span: Optional[Any], exception: Exception) -> None:
        if span is not None and self.enabled and OTEL_AVAILABLE:
            span.record_exception(exception)


_tracer_instance: Optional[BuildToValueTracer] = None


def get_tracer() -> BuildToValueTracer:
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = BuildToValueTracer()
    return _tracer_instance


def trace_task_execution(task_desc: str, task_id: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            attributes = {
                "btv.task.id": task_id,
                "btv.task.description": task_desc,
                "btv.phase": "2",
            }

            with tracer.start_span("btv.task.execute", attributes=attributes) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    if span is not None:
                        span.set_attribute("btv.task.duration", duration)
                        span.set_attribute("btv.task.status", "success")
                    return result
                except Exception as exc:  # pragma: no cover - error path
                    duration = time.time() - start_time
                    if span is not None:
                        span.set_attribute("btv.task.duration", duration)
                        span.set_attribute("btv.task.status", "failure")
                        span.set_attribute("btv.task.error", str(exc))
                        tracer.record_exception(span, exc)
                    raise

        return wrapper

    return decorator


def _pretty_print_config(config: Dict[str, Any]) -> str:
    return json.dumps(config, indent=2, ensure_ascii=False)


def main() -> int:
    tracer = get_tracer()

    if not tracer.enabled:
        print("⚠️ Telemetria desabilitada ou OpenTelemetry indisponível.")
        return 0

    with tracer.start_span("btv.tracer.selftest", {"test.key": "test.value"}) as span:
        tracer.add_event(span, "test.event", {"event.type": "selftest"})
        time.sleep(0.05)

    if tracer.config:
        print(_pretty_print_config(tracer.config))

    print("✅ Tracer funcionando corretamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
