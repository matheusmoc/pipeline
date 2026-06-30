"""
Instrumentacao Prometheus.

Configura a coleta automatica de metricas HTTP da aplicacao FastAPI
e expoe no endpoint /metrics para que o Prometheus faca o scrape.

Metricas coletadas automaticamente:
    - http_requests_total
    - http_request_duration_seconds
    - http_request_size_bytes
    - http_response_size_bytes
"""

from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    """
    Inicializa o instrumentador Prometheus na aplicacao.
    """
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=False,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)
